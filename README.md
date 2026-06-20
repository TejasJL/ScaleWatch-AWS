<div align="center">

<img src="https://img.shields.io/badge/AWS-Auto%20Scaling-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-Flask-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Region-Mumbai%20ap--south--1-232F3E?style=for-the-badge&logo=amazonaws"/>
<img src="https://img.shields.io/badge/Status-Live-10b981?style=for-the-badge"/>

# ⚡ ScaleWatch
### Live Auto-Scaling Web Dashboard on AWS

**A production-grade web application that automatically scales EC2 instances based on real CPU load — with a live dashboard showing exactly which server handled your request.**

[🌐 Live Demo](http://YOUR-ALB-DNS.ap-south-1.elb.amazonaws.com) · [📖 How It Works](#how-it-works) · [🚀 Deploy It Yourself](#deploy)

</div>

---

## 🎯 What Is This?

ScaleWatch is a Flask web application deployed on AWS that **demonstrates horizontal auto-scaling in real time**. When CPU load increases, AWS automatically launches new EC2 instances. When load drops, it removes them. The dashboard lets you **see this happening live** — which instance served your request, which availability zone it's in, and a load simulator that actually triggers scaling.
I built a web application on AWS that never crashes under traffic spikes — it auto-scales itself. The Application Load Balancer distributes requests across multiple EC2 instances in two availability zones. When CPU exceeds 60%, CloudWatch alarm fires and Auto Scaling launches a new EC2 instance within 2 minutes using a pre-configured Launch Template that automatically installs and starts the Flask app. The live dashboard shows which exact server handled your request — you can literally watch new instances spin up by clicking the load test button.

This project proves: **your app will never crash under traffic spikes because infrastructure scales itself.**

---

## ✨ Exact Features

| Feature | Description |
|---|---|
| 🎯 **Live Instance Tracker** | Every page load displays the EC2 instance ID, Availability Zone, instance type, and private IP that served your request |
| 🔄 **ALB Round-Robin Demo** | Refresh the page multiple times to watch load balancer distribute requests across different EC2 instances |
| 🔥 **Built-in Load Simulator** | Click "Launch Load Test" to fire 500 concurrent requests — actually triggers CloudWatch alarm and auto-scaling |
| 📊 **Request Counter** | Each EC2 instance tracks how many requests it has personally served |
| ⏱️ **Instance Uptime** | Shows how long the current instance has been running |
| 🖧 **Server Rack Visualizer** | Animated UI showing active instances, which one you're on, and when new ones are launching |
| 📋 **Live Activity Log** | Real-time log entries showing health checks, scaling triggers, and instance events |
| ✅ **Self-Healing** | If any EC2 instance fails ALB health check 3 times, Auto Scaling automatically replaces it |
| 🌐 **Multi-AZ** | Instances spread across ap-south-1a and ap-south-1b — survives one data center failure |
| 🔌 **REST API Endpoints** | `/health`, `/info`, `/stress` — usable for monitoring and testing |

---

## 🏗️ Architecture

```
                        ┌─────────────────────────────────────────┐
                        │           AWS ap-south-1 (Mumbai)        │
                        │                                          │
   Internet Users  ───► │  ┌──────────────────────────────────┐   │
   (HTTP :80)           │  │    Application Load Balancer      │   │
                        │  │         scalewatch-alb            │   │
                        │  │   • Internet-facing               │   │
                        │  │   • Listener: HTTP port 80        │   │
                        │  │   • Health check: GET /health     │   │
                        │  └──────────┬──────────┬─────────────┘   │
                        │             │          │                  │
                        │    ┌────────▼──┐  ┌───▼────────┐        │
                        │    │  EC2 #1   │  │  EC2 #2    │  ...   │
                        │    │ t2.micro  │  │ t2.micro   │        │
                        │    │ap-south-1a│  │ap-south-1b │        │
                        │    │Flask :5000│  │Flask :5000 │        │
                        │    └─────┬─────┘  └─────┬──────┘        │
                        │          └──────┬─────────┘              │
                        │                 │                         │
                        │  ┌──────────────▼──────────────────┐    │
                        │  │       Auto Scaling Group         │    │
                        │  │         scalewatch-asg           │    │
                        │  │   Min: 1  │  Desired: 2  │ Max: 4│   │
                        │  │   Scale OUT: CPU > 60%           │    │
                        │  │   Scale IN:  CPU < 40%           │    │
                        │  └──────────────┬──────────────────┘    │
                        │                 │                         │
                        │  ┌──────────────▼──────────────────┐    │
                        │  │         CloudWatch               │    │
                        │  │   AlarmHigh → fires → Scale Out  │    │
                        │  │   AlarmLow  → fires → Scale In   │    │
                        │  └──────────────┬──────────────────┘    │
                        │                 │                         │
                        │  ┌──────────────▼──────────────────┐    │
                        │  │        Launch Template           │    │
                        │  │   AMI: Amazon Linux 2023         │    │
                        │  │   Type: t2.micro                 │    │
                        │  │   UserData: git clone → gunicorn │    │
                        │  └─────────────────────────────────┘    │
                        │                                          │
                        │  VPC: scalewatch-vpc  10.0.0.0/16        │
                        │  ├─ Public Subnet 1  (ap-south-1a)       │
                        │  └─ Public Subnet 2  (ap-south-1b)       │
                        └─────────────────────────────────────────┘
```

---

## 🔄 How It Works

**Normal Flow (no load):**
1. User opens `http://ALB-DNS-NAME` in browser
2. ALB receives request on port 80
3. ALB checks which EC2 instances are healthy (via `/health` every 15s)
4. ALB picks an instance (round-robin) and forwards request to port 5000
5. Flask reads EC2 instance metadata and returns the dashboard
6. User sees exactly which EC2 instance and AZ served them

**Auto-Scaling Flow (under load):**
1. Load Simulator fires 500 requests (or you use `/stress` endpoint)
2. CPU across instances rises above 60%
3. CloudWatch `AlarmHigh` fires
4. Auto Scaling Group receives "scale out" signal
5. New EC2 instance launches using the Launch Template
6. Instance runs startup script: installs Python → clones GitHub repo → starts gunicorn
7. New instance passes ALB health checks (`/health` returns 200)
8. ALB starts routing traffic to the new instance
9. CPU drops → `AlarmLow` fires → instance count reduces back down

---

## 📁 File Structure

```
scalewatch-aws/
│
├── app.py                  # Flask backend — serves dashboard, handles routes
├── requirements.txt        # Python dependencies (Flask, Gunicorn, Requests)
├── userdata.sh             # EC2 launch script — runs on every new instance
├── .gitignore              # Excludes keys, cache, logs from git
│
├── templates/
│   └── index.html          # Frontend dashboard (Glassmorphism UI)
│
├── architecture/
│   └── workflow.png        # Architecture diagram
│
└── README.md               # This file
```

---

## 🛠️ AWS Services Used

| Service | Purpose |
|---|---|
| **EC2 t2.micro** | Runs the Flask web application |
| **Application Load Balancer** | Distributes HTTP traffic across healthy EC2 instances |
| **Auto Scaling Group** | Monitors CPU, launches/terminates EC2 instances automatically |
| **Launch Template** | Blueprint for new EC2 instances (AMI + type + startup script) |
| **Target Group** | ALB's list of healthy backends; runs health checks |
| **CloudWatch Alarms** | Fires when CPU > 60% (scale out) or < 40% (scale in) |
| **VPC + Subnets** | Isolated network across 2 availability zones |
| **Security Groups** | Firewall rules: ALB accepts port 80; EC2 accepts port 5000 from ALB only |

---

## 🚀 Deploy

### Prerequisites
- AWS Account (free tier)
- GitHub account
- Python 3.x installed locally

### Step-by-step Setup

**1. Fork and clone this repo**
```bash
git clone https://github.com/YOUR_USERNAME/scalewatch-aws.git
cd scalewatch-aws
```

**2. Create VPC**
- AWS Console → VPC → Create VPC and more
- Name: `scalewatch-vpc` | CIDR: `10.0.0.0/16`
- 2 AZs, 2 public subnets, no NAT gateway

**3. Create Security Groups**
```
scalewatch-alb-sg  →  Inbound: HTTP 80 from 0.0.0.0/0
scalewatch-ec2-sg  →  Inbound: TCP 5000 from scalewatch-alb-sg only
                       Inbound: SSH 22 from My IP
```

**4. Create Launch Template**
- AMI: Amazon Linux 2023 (free tier)
- Instance type: t2.micro
- User data: paste contents of `userdata.sh`
  (update the `git clone` URL to your repo first)

**5. Create Target Group**
- Protocol: HTTP | Port: 5000
- Health check path: `/health`
- Healthy threshold: 2 | Interval: 15s

**6. Create Application Load Balancer**
- Internet-facing | Both public subnets
- Security group: `scalewatch-alb-sg`
- Forward port 80 → target group

**7. Create Auto Scaling Group**
- Launch template: `scalewatch-template`
- Both public subnets
- Attach to: `scalewatch-tg`
- Min: 1 | Desired: 2 | Max: 4
- Target tracking: Average CPU = 60%

**8. Access your app**
```
http://YOUR-ALB-DNS-NAME.ap-south-1.elb.amazonaws.com
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Live dashboard — shows instance info, load simulator |
| `/health` | GET | ALB health check — returns `{"status": "healthy", "instance_id": "..."}` |
| `/info` | GET | Instance metadata JSON — ID, AZ, type, IP, uptime, request count |
| `/stress` | GET | Burns CPU for 25 seconds — triggers CloudWatch alarm and auto-scaling |

---

## 💡 Why This Project Is Useful

**Problem it solves:** A single server can only handle so many users. When traffic spikes (product launch, viral post), a single EC2 instance crashes.

**What this project demonstrates:**
- **Availability** — App stays online even if one EC2 instance or entire AZ fails
- **Scalability** — Handles 10x traffic without any manual intervention
- **Cost efficiency** — Automatically removes extra instances when not needed
- **Self-healing** — Unhealthy instances replaced automatically without human involvement

**Real-world use cases:** Any web app expecting variable traffic — e-commerce sales, news sites, SaaS platforms, APIs.

---

## ⚠️ Cost & Cleanup

**Estimated cost for 2-hour test:** ~$0.30–0.60 (ALB hourly rate)

**Delete all resources after testing (in this order):**
```
1. Auto Scaling Group     → EC2 → Auto Scaling Groups → Delete
2. Load Balancer          → EC2 → Load Balancers → Delete  
3. Target Group           → EC2 → Target Groups → Delete
4. Launch Template        → EC2 → Launch Templates → Delete
5. CloudWatch Alarms      → CloudWatch → Alarms → Delete both
6. VPC                    → VPC → Your VPCs → Delete VPC
```

---


<div align="center">
Built with ❤️ on AWS · Region: ap-south-1 (Mumbai)
<br/>
EC2 · ALB · Auto Scaling · CloudWatch · VPC
</div>
