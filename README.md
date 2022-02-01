# SaaS Integration
Refer to the folder "__SaaS_Integration" folder for the guideline for setting up a sample SaaS Integration system in Azure.
The system includes: 
- GitLab with CI/CD: host the whole repo (Microservices with Kafka)
- Jenkin CI/CD: test the serivices and deploy them as containers
- Confluence and Jira
- Tomcat 
- SonarQube for static analysis

# 3855_Kafka
Deploy a sample Microservices with Kafka services

---------------------------------------------------
Recommending Environment
- Ubuntu:18.04 or Ubuntu:20.04
- Docker package installed

---------------------------------------------------
- The project was run and tested on my personal Azure VM. Please adjust the setting (DNS URL) of your server:
+ app_conf of all services
+ EndpointAudit.js and AppStats.js
+ docker-compose.yaml

- Prerequisites directories, please adjust your home folder path in the docker-compose file 
+ <HOME>/config/<service_name>
+ <HOME>/logs
+ <HOME>/nginx

---------------------------------------------------
Running steps:
1) Clone the git repo
2) "cd" to each service folder (except nginx and deployment), run the command:
  $ docker build -t <service_name>:latest .   
  For example,
  ```# docker build -t processing:latest . ``` (make sure you have the "dot" at the end)

3) a) Copy the nginx.conf to the folder <HOME>/nginx on the server
   b) Copy log_conf.yaml and app_conf.yaml of each service to the associated folder on server <HOME>/config/<service_name>	

4) At the root directory where the docker-compose.yaml file locates, run:
  $ docker-compose up -d
  
  a) Verify all services are up and do not have the "Restarting" status
  $ docker ps -a
  b) Verify and observe the logs in the logs folder of each service
  
5) Navigate to your site and verify the dashboard is up. The stats has not been started.

6) Testing services using Apache JMeter (on any workstation that has Java 8).
  ##### Download JMeter at https://jmeter.apache.org/download_jmeter.cgi
  Import the Storage.jmx and run
  => The page shows the stats changing every 2 seconds
