from database import SessionLocal
from models import User, ServiceRequest, ServiceRequestStatus

db = SessionLocal()
plumbers = db.query(User).filter(User.role == 'gig_worker', User.expertise.ilike('%plumbing%')).all()

print("PLUMBERS:")
for p in plumbers:
    active_jobs = db.query(ServiceRequest).filter(
        ServiceRequest.assigned_worker_id == p.id,
        ServiceRequest.status.in_([ServiceRequestStatus.ASSIGNED, ServiceRequestStatus.IN_PROGRESS])
    ).all()
    print(f"- {p.full_name} (ID: {p.id}): {len(active_jobs)} active jobs")
    for job in active_jobs:
        print(f"   -> Job #{job.id}: {job.title}")

print("\nALL PLUMBING REQUESTS:")
requests = db.query(ServiceRequest).filter(ServiceRequest.service_type.ilike('%plumbing%')).all()
for r in requests:
    worker_name = r.assigned_worker.full_name if r.assigned_worker else "Unassigned"
    print(f"Request #{r.id} ({r.status}): Assigned to {worker_name}")

db.close()
