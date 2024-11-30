FROM php:8.1-apache

# Install MySQL extension
RUN docker-php-ext-install mysqli

# Enable mod_rewrite and allow .htaccess files
RUN a2enmod rewrite
# Enable mod_headers for controlling headers
RUN a2enmod headers

RUN sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

# Copy custom configuration file
COPY cors-disable.conf /etc/apache2/sites-available/000-default.conf

# Copy application code
COPY . /var/www/html/


# Expose the backend port
EXPOSE 80
