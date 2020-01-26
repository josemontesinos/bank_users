-- Create user
CREATE USER bankdbuser WITH PASSWORD 'bankdbpw';
ALTER ROLE bankdbuser SET client_encoding TO 'utf8';
ALTER ROLE bankdbuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE bankdbuser SET timezone TO 'UTC';
ALTER USER bankdbuser CREATEDB;

-- Create database
CREATE DATABASE bank WITH
  TEMPLATE template0
  ENCODING 'utf8'
  LC_COLLATE 'en_US.utf8'
  LC_CTYPE 'en_US.utf8'
  OWNER bankdbuser;

-- Connect to newly created database
\c bank

-- Create django schema
CREATE SCHEMA IF NOT EXISTS django AUTHORIZATION bankdbuser;
ALTER DATABASE bank SET search_path TO django;
DROP SCHEMA public;