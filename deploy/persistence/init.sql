-- Initialize user and database for KeyCloak

CREATE ROLE keycloak
WITH
    LOGIN
    PASSWORD 'keycloakPassword';

CREATE DATABASE keycloak
    OWNER keycloak
    ENCODING 'UTF8'
    TEMPLATE template0;

\connect keycloak;

GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;

GRANT ALL ON SCHEMA public TO keycloak;
ALTER SCHEMA public OWNER TO keycloak;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO keycloak;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO keycloak;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON FUNCTIONS TO keycloak;