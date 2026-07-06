# Scaling Guide

This guide details the horizontal scalability of EvalForge's stateless backend components and how to scale task workers.

---

## 1. Stateless API Layer

The backend is fully stateless:
* Session states are stored in JWT tokens or Redis.
* Request routing is round-robin or least-connections; sticky sessions are not required.
* Horizontal Pod Autoscaling (HPA) in Kubernetes should scale pods based on CPU/Memory utilization (target 70%).

---

## 2. Horizontal Scaling of Workers

Background tasks and jobs are pulled dynamically from Redis queues.
* Increase throughput by scaling the worker replica count.
* Avoid job duplication using Redis lock mechanisms.
* Implement dedicated pools of workers for specific high-priority queues.

---

## 3. Database Scaling & Partitioning

* **Read Replicas**: Configure the application's read operations to load-balance across multi-AZ Postgres read replicas.
* **Database Partitioning**: Segment evaluation metrics, records, and logs tables by date/month to prevent slow query execution times.
