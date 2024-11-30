import React, { useState, useEffect } from 'react';

function App() {
  const [users, setUsers] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [orders, setOrders] = useState([]);
  const [newOrder, setNewOrder] = useState({
    user_id: '',
    product_id: '',
    quantity: '',
  });
  const [messages, setMessages] = useState([]); // To handle multiple error/success messages

  useEffect(() => {
    const fetchData = async () => {
      const errors = [];
      try {
        // Fetch users
        const userResponse = await fetch('http://localhost:5001/users');
        if (!userResponse.ok) {
          throw new Error('Failed to fetch users');
        }
        const userData = await userResponse.json();
        setUsers(userData);
      } catch (error) {
        errors.push(`Users: ${error.message}`);
      }

      try {
        // Fetch catalog items
        const catalogResponse = await fetch('http://localhost:5002/books');
        if (!catalogResponse.ok) {
          throw new Error('Failed to fetch catalog');
        }
        const catalogData = await catalogResponse.json();
        setCatalog(catalogData);
      } catch (error) {
        errors.push(`Catalog: ${error.message}`);
      }

      try {
        // Fetch orders
        const orderResponse = await fetch('http://localhost:5003/orders');
        if (!orderResponse.ok) {
          throw new Error('Failed to fetch orders');
        }
        const orderData = await orderResponse.json();
        setOrders(orderData);
      } catch (error) {
        errors.push(`Orders: ${error.message}`);
      }

      setMessages(errors);
    };

    fetchData();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewOrder({ ...newOrder, [name]: value });
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate input
    if (!newOrder.user_id || !newOrder.product_id || !newOrder.quantity) {
      setMessages(['Please fill in all the fields.']);
      return;
    }

    const orderData = { ...newOrder, status: 'Pending' }; // Add status as "Pending"

    try {
      const response = await fetch('http://localhost:5003/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to place order');
      }

      const data = await response.json();
      data.id=data.order_id;
      data.product_id = newOrder.product_id;
      data.quantity = newOrder.quantity;
      data.status="Pending";
      data.user_id=newOrder.user_id;
      setMessages([`Order placed successfully with ID: ${data.order_id}`]);
      setOrders([...orders, data]); // Add the new order to the list
      setNewOrder({ user_id: '', product_id: '', quantity: '' }); // Reset the form
    } catch (error) {
      setMessages([`Error: ${error.message}`]);
    }
  };

  return (
    <div>
      <h1>Service Dashboard</h1>

      {messages.map((msg, index) => (
        <p key={index}>{msg}</p>
      ))}

      <h2>Users</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            {user.username} - {user.email}
          </li>
        ))}
      </ul>

      <h2>Catalog</h2>
      <ul>
        {catalog.map((item) => (
          <li key={item.id}>
            {item.title} - {item.author} - {item.stock}
          </li>
        ))}
      </ul>

      <h2>Orders</h2>
      <ul>
        {orders.map((order) => (
          <li key={order.id}>
            Order ID: {order.id}, Product ID: {order.product_id}, Quantity:{' '}
            {order.quantity}, Status: {order.status}
          </li>
        ))}
      </ul>

      <h2>Place a New Order</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            User:
            <select
              name="user_id"
              value={newOrder.user_id}
              onChange={handleInputChange}
              required
            >
              <option value="">Select a user</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.username}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div>
          <label>
            Product:
            <select
              name="product_id"
              value={newOrder.product_id}
              onChange={handleInputChange}
              required
            >
              <option value="">Select a product</option>
              {catalog.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div>
          <label>
            Quantity:
            <input
              type="number"
              name="quantity"
              value={newOrder.quantity}
              onChange={handleInputChange}
              required
              min="1"
            />
          </label>
        </div>
        <button type="submit">Place Order</button>
      </form>
    </div>
  );
}

export default App;
