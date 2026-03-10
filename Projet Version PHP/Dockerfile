FROM php:8.2-apache

# Installer extensions PHP nécessaires
RUN apt-get update && apt-get install -y libpq-dev unzip git && docker-php-ext-install pdo pdo_pgsql pgsql

# Activer mod_rewrite
RUN a2enmod rewrite

# Droits
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
