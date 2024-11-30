<?php

header("Content-Type: application/json");

// Database Configuration
$host = getenv("DB_HOST") ?: "localhost";
$user = getenv("DB_USER") ?: "order_service_user";
$password = getenv("DB_PASS") ?: "order_service_pass";
$database = getenv("DB_NAME") ?: "order_service_db";

// Database Connection
$mysqli = new mysqli($host, $user, $password, $database);

if ($mysqli->connect_error) {
    error_log("Database connection failed: " . $mysqli->connect_error);
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit;
}

/**
 * Send a JSON response with a specific HTTP status code.
 *
 * @param array $data
 * @param int $statusCode
 */
function jsonResponse($data, $statusCode = 200) {
    http_response_code($statusCode);
    echo json_encode($data);
    exit;
}

// Utility Functions
function validateId($id, $name = 'ID') {
    if ($id === null || !is_int($id) || $id <= 0) {
        jsonResponse(["error" => "$name must be a positive integer"], 400);
    }
}

function validateFields($data, $requiredFields) {
    foreach ($requiredFields as $field) {
        if (!isset($data[$field])) {
            jsonResponse(["error" => "Missing required field: $field"], 400);
        }
    }
}

function validateUser($user_id) {
    $userServiceUrl = "http://user-service:5001/users/$user_id";
    $response = @file_get_contents($userServiceUrl);
    if ($response === false) {
        error_log("Failed to validate user with ID: $user_id");
        return false;
    }
    $user = json_decode($response, true);
    return isset($user['id']) && $user['id'] == $user_id;
}

function validateProduct($product_id) {
    $productServiceUrl = "http://catalog-service:5000/books/$product_id";
    $response = @file_get_contents($productServiceUrl);

    if ($response === false) {
        error_log("Failed to fetch product with ID: $product_id");
        return false;
    }

    $productData = json_decode($response, true);
    if (!isset($productData['stock'])) {
        error_log("Product data does not contain stock information for product ID: $product_id");
        return false;
    }

    return $productData;
}

/**
 * Update the product stock in the catalog service.
 *
 * @param int $product_id
 * @param int $newStock
 * @return bool
 */
function updateProductStock($product_id, $newStock) {
    $catalogServiceUrl = "http://catalog-service:5000/books/updatestock/$product_id";
    $payload = json_encode(['stock' => $newStock]);

    $options = [
        'http' => [
            'header'  => "Content-Type: application/json\r\n",
            'method'  => 'PUT',
            'content' => $payload,
        ],
    ];

    $context = stream_context_create($options);
    $response = @file_get_contents($catalogServiceUrl, false, $context);

    if ($response === false) {
        $error = error_get_last();
        error_log("Failed to update stock for product ID: $product_id. Error: " . $error['message']);
        return false;
    }

    $responseData = json_decode($response, true);
    if (isset($responseData['error'])) {
        error_log("Error updating stock for product ID $product_id: " . $responseData['error']);
        return false;
    }

    return true;
}

// Routing Logic
$requestUri = $_SERVER['REQUEST_URI'];
$requestMethod = $_SERVER['REQUEST_METHOD'];
$routeParams = [];

if (preg_match('/^\/orders(?:\/(\d+))?$/', $requestUri, $matches)) {
    $routeParams['order_id'] = isset($matches[1]) ? (int)$matches[1] : null;
} else {
    http_response_code(404);
    echo json_encode(["error" => "Invalid endpoint"]);
    exit;
}

// Endpoints

// Retrieve All Orders
if ($requestMethod === 'GET' && $routeParams['order_id'] === null) {
    $result = $mysqli->query("SELECT * FROM orders");
    jsonResponse($result->fetch_all(MYSQLI_ASSOC));
}

// Retrieve a Specific Order
if ($requestMethod === 'GET' && $routeParams['order_id'] !== null) {
    $order_id = $routeParams['order_id'];
    validateId($order_id, 'Order ID');

    $stmt = $mysqli->prepare("SELECT * FROM orders WHERE id = ?");
    $stmt->bind_param("i", $order_id);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($order = $result->fetch_assoc()) {
        jsonResponse($order);
    } else {
        jsonResponse(["error" => "Order not found"], 404);
    }

    $stmt->close();
}

// Create a New Order
if ($requestMethod === 'POST' && preg_match('~^/orders/?$~', $requestUri)) {
    $data = json_decode(file_get_contents('php://input'), true);
    validateFields($data, ['user_id', 'product_id', 'quantity', 'status']);

    $user_id = $data['user_id'];
    $product_id = $data['product_id'];
    $quantity = $data['quantity'];

    // Validate the user
    if (!validateUser($user_id)) {
        jsonResponse(["error" => "User not found"], 400);
    }

    // Validate the product
    $productData = validateProduct($product_id);
    if (!$productData) {
        jsonResponse(["error" => "Product not found"], 400);
    }

    // Check stock availability
    if ($productData['stock'] < $quantity) {
        jsonResponse(["error" => "Insufficient stock for the product"], 400);
    }

    // Insert the order
    $stmt = $mysqli->prepare("INSERT INTO orders (user_id, product_id, quantity, status) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("iiis", $user_id, $product_id, $quantity, $data['status']);

    if ($stmt->execute()) {
        $orderId = $stmt->insert_id;
        $newStock = $productData['stock'] - $quantity;

        if (updateProductStock($product_id, $newStock)) {
            jsonResponse(["message" => "Order created successfully", "order_id" => $orderId], 201);
        } else {
            $mysqli->query("DELETE FROM orders WHERE id = $orderId");
            jsonResponse(["error" => "Failed to update product stock. Order creation rolled back."], 500);
        }
    } else {
        jsonResponse(["error" => "Failed to create order: " . $stmt->error], 500);
    }

    $stmt->close();
}

// Delete an Order
if ($requestMethod === 'DELETE' && $routeParams['order_id'] !== null) {
    $order_id = $routeParams['order_id'];
    validateId($order_id, 'Order ID');

    $stmt = $mysqli->prepare("DELETE FROM orders WHERE id = ?");
    $stmt->bind_param("i", $order_id);

    if ($stmt->execute()) {
        jsonResponse(["message" => "Order deleted successfully"]);
    } else {
        jsonResponse(["error" => "Failed to delete order: " . $stmt->error], 500);
    }

    $stmt->close();
}

jsonResponse(["error" => "Endpoint not found"], 404);

?>
