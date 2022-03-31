# Digital Ocean Deployment

## Requirements

The region you want to use in Digital Ocean needs to support managed databases and Load Balancers.
You will have to manage DNS in Digital Ocean to utilize automatic certificate generation, otherwise
you will have to provide your own certificate for the Load Balancer or modify the droplets to handle
SSL termination.

## General notes and advice

-   always create resources in the same datacenter region

## 1. Create a VPC

https://cloud.digitalocean.com/networking/vpc

Create a VPC named `iscc-service-generator` in your preferred region.

## 2. Create a managed Postgres database

https://cloud.digitalocean.com/databases/new?engine=pg

Create a PostgreSQL 14 managed database cluster named `db-iscc-service-generator`. **Make sure to
select the correct VPC you created earlier!**

Continue with the other steps while the database is provisioning.

## 3. Create a Firewall

https://cloud.digitalocean.com/networking/firewalls

Create a Firewall named `iscc-service-generator-node`. Leave the default settings:

-   allow inbound SSH
-   allow outbound ICMP
-   allow outbound all TCP
-   allow outbound all UDP

## 4. Create a Load Balancer

https://cloud.digitalocean.com/networking/load_balancers

Create a new Load Balancer, again making sure to select the same datacenter region and VPC.

Leave the droplet names/tags empty for now.

Leave the default forwarding rule for HTTP port 80 -> HTTP port 80.

Add a new forwarding rule for HTTPS port 443 -> HTTP port 80. In "Certificate", select "+ New
certificate". Under "Use Let's Encrypt" select the domain you intend to use and select "Include all
subdomains". Name the certificate `iscc-service-generator` and click "Generate".

Keep all other settings as default and create the Load Balancer with name
`lb-iscc-service-generator`.

Continue with the other steps while the Load Balancer is being created.

## 5. Create PostgreSQL database and user

https://cloud.digitalocean.com/databases/db-iscc-service-generator

Under "Connection details", select "Connection string" instead of "Connection parameters". Click
"show-password". Copy/note down the connection string (make sure to keep this secure or remove all
traces when done as this allows admin access to the database!).

Note: In case the database is still provisioning, wait until it is done.

It is not possible to create unpriviledged users via the Digital Ocean UI, so creating the database
and user has do be done manually. These steps do this by running a postgres Docker image locally,
but all other ways to access a PostgreSQL directly should work too.

Open a POSIX shell on your local device (bash, zsh, …):

1. run `docker run --rm -it postgres:14 bash`
2. set the database connection string you copied earlier with `read DATABASE_URL` (paste it and
   confirm with enter)
3. run `psql $DATABASE_URL`
4. a `defaultdb=>` prompt should appear
5. create a database with `create database iscc_service_generator;`
6. create a user with `create user iscc_service_generator with encrypted password 'mypass';`
   (replace mypass with a secure password and note it down)
7. give the new user all privileges on the new database:
   `grant all privileges on database iscc_service_generator to iscc_service_generator;`
8. exit the psql shell and Docker container by entering `exit` twice.

Open the database management interface again and copy the connection string for the new
user/database. Under "Connection details", select "VPC network" instead of "Public network" and
"Connection string" instead of "Connection parameters". Select the user and database you created
earlier (iscc_service_generator) in both dropdowns below the connection string. Show password won't
work here because the management UI has no knowledge of the password created via psql. Copy the
connection string and modify it with the correct password used when creating the user. Note this
down, you will need it later.

## 6. Create a Space

https://cloud.digitalocean.com/spaces

Create a new Space in the correct region and choose a unique name. No suggestion here as these names
are globally unique.

Make sure "Restrict File Listing" is enabled.

Create an access key for Spaces in https://cloud.digitalocean.com/account/api/tokens and note down
both the key and the secret key.

## 5. Create backend and worker droplets

https://cloud.digitalocean.com/droplets/new?size=s-1vcpu-1gb&region=ams3&distro=debian&distroImage=debian-11-x64

Create a new Droplet with Debian 11, again making sure to select the same datacenter region and VPC.

Configure the authentication as required, SSH keys are recommended.

Enable Monitoring and User data in the additional options.

### 5.1. User data for backend droplets

Paste the contents of [userdata-backend.sh](userdata-backend.sh) into the user data text field.
Update the variables according to the credentials you noted down earlier.

Name the droplet(s) `iscc-service-generator-backend-01` (increase the number at the and as
required).

Add the tag `iscc-service-generator-backend`.

Create the droplet(s) and continue with creating worker droplets.

### 5.2. User data for worker droplets

Paste the contents of [userdata-worker.sh](userdata-worker.sh) into the user data text field. Update
the variables according to the credentials you noted down earlier.

Name the droplet(s) `iscc-service-generator-worker-01` (increase the number at the and as required).

Add the tag `iscc-service-generator-worker`.

Create the droplet(s) and continue.

## 6. Finalize database configuration

https://cloud.digitalocean.com/databases/db-iscc-service-generator

Open the database configuration again. Open the "Settings" tab and edit the "Trusted sources". Enter
the tags `iscc-service-generator-backend` and `iscc-service-generator-worker` and click on "Save" to
only allow droplets tagged with those tags to access the database.

This will automatically affect all new droplets created with those tags, no need to update the
database again.

## 7. Finalize Load Balancer configuration

https://cloud.digitalocean.com/networking/load_balancers

Open the Load Balancer configuration again. Click on "Choose Droplets" and enter the tag
`iscc-service-generator-backend` you used when creating the backend droplet(s).

Click on "Add Droplets", the created backend droplets should appear in the table.

This will automatically affect all new droplets created with those tags, no need to update the Load
Balancer again.

Open the "Settings" tab and edit the Health checks configuration. Change "Path" from "/" to
"/api/docs" and click on "Save".

## 8. Finalize Firewall configuration

https://cloud.digitalocean.com/networking/firewalls

Open the Firewall configuration again. Open the "Droplets" tab, click on "Add Droplets" and enter
the tags `iscc-service-generator-backend` and `iscc-service-generator-worker` you used when creating
the backend droplet(s). All worker and backend droplets you created should appear in the table
below.

Open the "Rules" tab, add a new HTTP rule, remove everything from the "Sources" input and enter the
Load Balancer name (`lb-iscc-service-generator`) and click on "Save" to allow it to access the HTTP
port on the droplets.

This will automatically affect all new droplets created with those tags, no need to update the
Firewall again.

## 9. Update DNS

https://cloud.digitalocean.com/networking/domains

Open the domain you intend to run the service with. Add a new A record on the subdomain you wish to
run the service under and select the Load Balancer you created earlier (`lb-iscc-service-generator`)
in "will redirect to" and click on "Create Record".

## 10. Create initial login data

Open a shell on one of the backend droplets (either via SSH or the web console). Navigate to
`/iscc-service-generator` and run the following command to create an admin user:

`docker compose run --rm backend python -m dev.install`

Note down the username and password and try to login on the configured domain under
`/dashboard/login`.
