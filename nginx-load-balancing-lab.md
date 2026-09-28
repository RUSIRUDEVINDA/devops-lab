# Nginx Load Balancing, Failover, and High Availability Lab

## 1. Objective

The goal of this lab is to understand how a load balancer distributes traffic between multiple backend servers and what happens when one backend server becomes unavailable.

In this lab, I will:

- Create two backend web servers
- Run each backend on a different port
- Install and configure Nginx
- Configure Nginx as a load balancer
- Observe round-robin load balancing
- Simulate backend failure
- Test failover behavior
- Use Linux troubleshooting tools such as `curl`, `ss`, `systemctl`, `journalctl`, and Nginx logs

---

# 2. Architecture

The lab will run on one Linux virtual machine.

Even though there is only one VM, there will be three separate web server processes:

```text
                    Client
                      |
                      |
                      v
                  Nginx
                  Port 80
                    |
             +------+------+
             |             |
             v             v
        Backend 1       Backend 2
        Port 8080       Port 8081
```

Nginx receives requests on port `80`.

Nginx then forwards those requests to either:

```text
127.0.0.1:8080
```

or:

```text
127.0.0.1:8081
```

---

# 3. What Is a Backend Server?

A backend server is a server or application that receives requests from another server such as a load balancer or reverse proxy.

For example:

```text
User
 |
 v
Nginx
 |
 v
Application
```

The application behind Nginx is the backend.

In this lab, the two backend servers are simple Python HTTP servers.

They will run as two separate Linux processes.

```text
Python process 1
 |
 v
Port 8080
```

and:

```text
Python process 2
 |
 v
Port 8081
```

This means a backend does not always need to be a completely separate physical server.

Later, the same architecture could use:

```text
Backend VM 1
Backend VM 2
```

or:

```text
Docker Container 1
Docker Container 2
```

or Kubernetes Pods.

---

# 4. Prerequisites

The Linux VM should have:

- Ubuntu or another Linux distribution
- Python 3
- sudo access
- Internet access for installing Nginx

Check Python:

```bash
python3 --version
```

Expected output should look similar to:

```text
Python 3.x.x
```

---

# 5. Create the Lab Directory

Create the main lab directory:

```bash
mkdir -p ~/load-balancer-lab
```

Create two backend directories:

```bash
mkdir -p ~/load-balancer-lab/backend1
mkdir -p ~/load-balancer-lab/backend2
```

Check the structure:

```bash
tree ~/load-balancer-lab
```

Expected:

```text
load-balancer-lab
├── backend1
└── backend2
```

If `tree` is not installed:

```bash
sudo apt update
sudo apt install tree -y
```

---

# 6. Create Backend 1

Create an HTML file:

```bash
cat > ~/load-balancer-lab/backend1/index.html <<'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Backend 1</title>
</head>
<body>
    <h1>Hello from Backend 1</h1>
    <p>This request was served by Backend 1.</p>
    <p>Port: 8080</p>
</body>
</html>
EOF
```

Check the file:

```bash
cat ~/load-balancer-lab/backend1/index.html
```

---

# 7. Create Backend 2

Create another HTML file:

```bash
cat > ~/load-balancer-lab/backend2/index.html <<'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Backend 2</title>
</head>
<body>
    <h1>Hello from Backend 2</h1>
    <p>This request was served by Backend 2.</p>
    <p>Port: 8081</p>
</body>
</html>
EOF
```

Check it:

```bash
cat ~/load-balancer-lab/backend2/index.html
```

The pages are intentionally different.

This makes it easy to identify which backend processed each request.

---

# 8. Start Backend 1

Open Terminal 1.

Move into the Backend 1 directory:

```bash
cd ~/load-balancer-lab/backend1
```

Start a Python HTTP server:

```bash
python3 -m http.server 8080
```

Expected output:

```text
Serving HTTP on 0.0.0.0 port 8080
```

This command starts a web server.

The important part is:

```text
8080
```

The process is now listening for network connections on TCP port `8080`.

Do not close this terminal.

---

# 9. Start Backend 2

Open Terminal 2.

Run:

```bash
cd ~/load-balancer-lab/backend2
```

Start the second server:

```bash
python3 -m http.server 8081
```

Expected:

```text
Serving HTTP on 0.0.0.0 port 8081
```

Now there are two separate backend processes.

```text
Backend 1 → 8080
Backend 2 → 8081
```

---

# 10. Verify the Backends

Open Terminal 3.

Test Backend 1:

```bash
curl localhost:8080
```

Expected response should contain:

```text
Hello from Backend 1
```

Now test Backend 2:

```bash
curl localhost:8081
```

Expected response should contain:

```text
Hello from Backend 2
```

At this stage:

```text
curl localhost:8080
        |
        v
    Backend 1
```

and:

```text
curl localhost:8081
        |
        v
    Backend 2
```

---

# 11. What Is curl?

`curl` is a command-line HTTP client.

It allows us to send HTTP requests without opening a web browser.

Example:

```bash
curl http://localhost:8080
```

This sends an HTTP request to:

```text
localhost
```

on:

```text
port 8080
```

`localhost` normally refers to:

```text
127.0.0.1
```

which means the current machine.

---

# 12. Check Listening Ports

Run:

```bash
ss -lnt
```

Options:

```text
-l = listening sockets
-n = show numeric ports
-t = TCP connections
```

You should see entries containing:

```text
8080
8081
```

For more process information:

```bash
sudo ss -lntp
```

The `-p` option shows which process owns the socket.

Conceptually:

```text
Port 8080
   |
   v
Python process

Port 8081
   |
   v
Python process
```

---

# 13. Install Nginx

Install Nginx:

```bash
sudo apt update
sudo apt install nginx -y
```

Check the service:

```bash
systemctl status nginx
```

Expected:

```text
active (running)
```

Check whether it starts automatically at boot:

```bash
systemctl is-enabled nginx
```

Expected:

```text
enabled
```

---

# 14. Test Nginx Before Configuration

Run:

```bash
curl localhost
```

Since no port is specified, HTTP defaults to:

```text
port 80
```

So this is equivalent to:

```bash
curl localhost:80
```

At this point, the default Nginx page should appear.

Now the server has three listening ports:

```text
80    → Nginx
8080  → Backend 1
8081  → Backend 2
```

Verify:

```bash
sudo ss -lntp
```

---

# 15. What Is a Load Balancer?

A load balancer sits in front of multiple backend servers.

Instead of users connecting directly to each backend:

```text
User → Backend 1
User → Backend 2
```

the user connects to one frontend endpoint:

```text
User
 |
 v
Load Balancer
 |        |
 v        v
B1       B2
```

The load balancer decides where each request should go.

Benefits include:

- distributing traffic
- reducing load on individual servers
- improving availability
- allowing backend maintenance
- reducing dependency on one backend

---

# 16. Configure Nginx as a Load Balancer

Create a new configuration:

```bash
sudo nano /etc/nginx/sites-available/load-balancer
```

Add:

```nginx
upstream backend_servers {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend_servers;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Save the file.

---

# 17. Understanding the Nginx Configuration

This section:

```nginx
upstream backend_servers {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
}
```

creates an upstream group named:

```text
backend_servers
```

The group contains two backend servers.

Backend 1:

```text
127.0.0.1:8080
```

Backend 2:

```text
127.0.0.1:8081
```

This section:

```nginx
server {
    listen 80;
```

means Nginx listens for incoming HTTP requests on port `80`.

This:

```nginx
location / {
```

matches requests to the root URL and paths below it.

For example:

```text
/
```

or:

```text
/test
```

This line:

```nginx
proxy_pass http://backend_servers;
```

tells Nginx to forward requests to the backend group.

---

# 18. Understanding Proxy Headers

The configuration also contains:

```nginx
proxy_set_header Host $host;
```

This forwards the original hostname.

This:

```nginx
proxy_set_header X-Real-IP $remote_addr;
```

passes the client's IP address.

And:

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

keeps information about the request path through proxy servers.

These headers become very important in real production systems.

---

# 19. Enable the New Nginx Configuration

Disable the default site:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Enable the new site:

```bash
sudo ln -s /etc/nginx/sites-available/load-balancer /etc/nginx/sites-enabled/load-balancer
```

Check:

```bash
ls -l /etc/nginx/sites-enabled/
```

You should see something similar to:

```text
load-balancer -> /etc/nginx/sites-available/load-balancer
```

---

# 20. Test the Nginx Configuration

Before applying configuration changes, always run:

```bash
sudo nginx -t
```

Expected:

```text
syntax is ok
test is successful
```

This is an important operational practice.

Never blindly restart Nginx after editing configuration.

A syntax error could prevent Nginx from starting correctly.

---

# 21. Reload Nginx

Apply the configuration:

```bash
sudo systemctl reload nginx
```

Check:

```bash
systemctl status nginx
```

---

# 22. Test Load Balancing

Run:

```bash
curl localhost
```

Run it again:

```bash
curl localhost
```

Then again.

You should observe responses alternating between:

```text
Hello from Backend 1
```

and:

```text
Hello from Backend 2
```

For example:

```text
Request 1 → Backend 1
Request 2 → Backend 2
Request 3 → Backend 1
Request 4 → Backend 2
```

This behavior is called:

```text
Round Robin Load Balancing
```

---

# 23. What Is Round Robin?

Round robin distributes requests sequentially across available backend servers.

Example:

```text
Backend A
Backend B
Backend C
```

Requests may be distributed like this:

```text
Request 1 → A
Request 2 → B
Request 3 → C
Request 4 → A
Request 5 → B
Request 6 → C
```

Nginx uses round robin by default when no other load-balancing algorithm is configured.

---

# 24. Automate the Test

Instead of running `curl` manually many times:

```bash
for i in {1..10}; do
    curl -s localhost
done
```

The `-s` option means silent mode.

The responses should alternate between Backend 1 and Backend 2.

---

# 25. Simulate Backend Failure

Now simulate a real production problem.

Stop Backend 1.

Go to the terminal running:

```bash
python3 -m http.server 8080
```

Press:

```text
Ctrl+C
```

Backend 1 is now unavailable.

---

# 26. Verify Backend 1 Is Down

Run:

```bash
curl localhost:8080
```

Expected:

```text
Failed to connect
```

Now test Backend 2:

```bash
curl localhost:8081
```

It should still respond.

---

# 27. Check Listening Ports Again

Run:

```bash
sudo ss -lntp
```

Previously:

```text
80
8080
8081
```

Now you should only see:

```text
80
8081
```

Port `8080` is missing because Backend 1 has stopped.

This is an important troubleshooting technique.

---

# 28. Test the Load Balancer During Failure

Run:

```bash
curl localhost
```

Repeat:

```bash
for i in {1..10}; do
    curl -s localhost
done
```

Nginx should continue serving traffic through Backend 2.

The architecture is now:

```text
                     Nginx
                    Port 80
                    /     \
                   /       \
                  v         v
            Backend 1   Backend 2
               DOWN        UP
               ❌          ✅
```

The application can still respond because another backend is available.

---

# 29. What Is Failover?

Failover means traffic or workload moves to another available system when one component fails.

Before failure:

```text
Nginx
 |
 +--> Backend 1
 |
 +--> Backend 2
```

After Backend 1 fails:

```text
Nginx
 |
 +--> Backend 1 ❌
 |
 +--> Backend 2 ✅
```

Traffic continues through Backend 2.

---

# 30. What Is High Availability?

High availability means designing systems to reduce downtime.

A single-server architecture has a major problem:

```text
Client
 |
 v
Server
```

If that server fails, the application is unavailable.

This is called a:

```text
Single Point of Failure
```

Using multiple backend servers reduces this risk.

```text
Client
 |
 v
Load Balancer
 |
 +--> Backend 1
 |
 +--> Backend 2
```

However, in this lab Nginx itself is still a single point of failure.

If Nginx goes down, the client cannot reach either backend.

Real high-availability systems therefore also add redundancy for the load-balancing layer.

---

# 31. Nginx Failure Handling

The upstream block can be changed to:

```nginx
upstream backend_servers {
    server 127.0.0.1:8080 max_fails=1 fail_timeout=10s;
    server 127.0.0.1:8081 max_fails=1 fail_timeout=10s;
}
```

`max_fails=1` means Nginx can treat the backend as unavailable after a failure.

`fail_timeout=10s` controls the failure window and temporary unavailable period.

After editing the configuration:

```bash
sudo nginx -t
```

Then:

```bash
sudo systemctl reload nginx
```

---

# 32. Passive Health Checks

In this simple open-source Nginx setup, failure detection is mainly passive.

This means Nginx learns that a backend is unhealthy when traffic to that backend fails.

Conceptually:

```text
Request
   |
   v
Nginx
   |
   v
Backend 1
   |
   X Connection failed
   |
   v
Nginx recognizes failure
```

This is different from an active health check system that continuously sends requests such as:

```text
GET /health
```

even when no user traffic exists.

---

# 33. Troubleshooting Workflow

If users report:

```text
"The application is down."
```

do not immediately restart everything.

Use a structured troubleshooting process.

## Step 1: Check Nginx

```bash
systemctl status nginx
```

Question:

```text
Is Nginx running?
```

---

## Step 2: Check Listening Ports

```bash
sudo ss -lntp
```

Check for:

```text
80
8080
8081
```

If port `8080` is missing, Backend 1 may be down.

---

## Step 3: Test Backend 1

```bash
curl localhost:8080
```

---

## Step 4: Test Backend 2

```bash
curl localhost:8081
```

---

## Step 5: Test Nginx

```bash
curl localhost
```

---

## Step 6: Validate Configuration

```bash
sudo nginx -t
```

---

## Step 7: Inspect Nginx Access Logs

```bash
sudo tail -f /var/log/nginx/access.log
```

The access log shows incoming HTTP requests.

---

## Step 8: Inspect Nginx Error Logs

```bash
sudo tail -f /var/log/nginx/error.log
```

This can show failures connecting to backend servers.

---

## Step 9: Inspect systemd Logs

```bash
journalctl -u nginx
```

For recent logs:

```bash
journalctl -u nginx --since "30 minutes ago"
```

---

# 34. Troubleshooting Logic

A useful DevOps troubleshooting flow is:

```text
Application unavailable
        |
        v
Is Nginx running?
        |
        v
Is port 80 listening?
        |
        v
Can Nginx reach Backend 1?
        |
        v
Can Nginx reach Backend 2?
        |
        v
Is the Nginx configuration valid?
        |
        v
Check logs
        |
        v
Find root cause
```

---

# 35. Useful Commands Learned

## Network

```bash
ss -lntp
```

Shows listening TCP ports and processes.

```bash
curl localhost
```

Tests HTTP connectivity.

---

## Nginx

```bash
sudo nginx -t
```

Tests Nginx configuration.

```bash
sudo systemctl reload nginx
```

Reloads Nginx configuration.

```bash
systemctl status nginx
```

Checks service status.

---

## Logs

```bash
journalctl -u nginx
```

Shows systemd logs.

```bash
sudo tail -f /var/log/nginx/access.log
```

Shows incoming requests.

```bash
sudo tail -f /var/log/nginx/error.log
```

Shows Nginx errors.

---

# 36. Important Concepts Learned

## Load Balancer

Distributes traffic between multiple backend servers.

## Backend

Application or server behind the load balancer.

## Reverse Proxy

A server that receives requests on behalf of backend servers and forwards them.

Nginx acts as both:

```text
Reverse Proxy
+
Load Balancer
```

## Round Robin

Sequentially distributes requests between backend servers.

## Failover

Traffic continues through another backend when one fails.

## Redundancy

Having more than one component capable of performing the same job.

## High Availability

Designing systems to minimize service downtime.

## Single Point of Failure

A component whose failure causes the entire service to become unavailable.

---

# 37. Final Architecture

```text
                      Client
                        |
                        |
                        v
                  Nginx :80
               Load Balancer
                   /    \
                  /      \
                 v        v
        Python Server   Python Server
           :8080           :8081
        Backend 1       Backend 2
```

Normal operation:

```text
Request 1 → Backend 1
Request 2 → Backend 2
Request 3 → Backend 1
Request 4 → Backend 2
```

Failure scenario:

```text
Backend 1 ❌

Requests continue through:

Backend 2 ✅
```

---

# 38. What I Learned

From this lab I learned how multiple backend servers can be placed behind an Nginx load balancer.

I learned how Nginx uses an upstream block to define backend servers and how `proxy_pass` forwards requests to those servers.

I observed Nginx's default round-robin behavior by sending repeated requests and seeing responses alternate between Backend 1 and Backend 2.

I also simulated a backend failure by stopping one Python HTTP server. I verified the failure using `curl` and `ss`, then observed that Nginx could continue serving requests using the remaining backend.

I practiced troubleshooting using:

```text
curl
ss
systemctl
journalctl
nginx -t
Nginx access logs
Nginx error logs
```

This lab helped me understand load balancing, failover, redundancy, reverse proxies, and high-availability concepts.

---

# 39. Next Improvements

This lab can be expanded later by:

- running each backend on a separate VM
- using Flask instead of static HTML
- containerizing each backend with Docker
- using Docker Compose
- adding health-check endpoints
- adding HTTPS
- configuring weighted load balancing
- configuring least-connections load balancing
- adding monitoring with Prometheus and Grafana
- deploying the same architecture in AWS
- replacing local backends with Kubernetes Pods
