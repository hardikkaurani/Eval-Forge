# Disaster Recovery Guide

This guide details database backup, snapshot, and restore protocols to maintain low RPO (Recovery Point Objective) and RTO (Recovery Time Objective).

---

## 1. Recovery Point Objective (RPO) & Recovery Time Objective (RTO)

* **RPO**: 1 hour (maximum data loss target).
* **RTO**: 30 minutes (maximum system restore target).

---

## 2. Backup & Snapshot Schedule

* **Database (PostgreSQL)**: Enable automated daily snapshots with 30-day retention and continuous WAL archiving to S3/GCS.
* **Configuration & Environment**: Store all infrastructure parameters, Helm configurations, and Kubernetes manifests in Git (GitOps).

---

## 3. Restore Procedures

### Database Recovery
1. Spin up a new PostgreSQL instance using the latest automated snapshot.
2. Apply Point-in-Time Recovery (PITR) to replay WAL logs up to the failure timestamp.
3. Update the backend API's database connection string environment variable to target the new master node.
4. Verify schema validity by running Alembic checks.
