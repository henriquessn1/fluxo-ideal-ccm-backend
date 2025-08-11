#!/usr/bin/env python
"""
Seed database with mock data for the new monitoring structure
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models import (
    Client, Instance, Module, Installation, 
    Endpoint, Threshold, MonitoringLog
)


def clear_database(db):
    """Clear all existing data"""
    print("Clearing existing data...")
    db.query(MonitoringLog).delete()
    db.query(Threshold).delete()
    db.query(Installation).delete()
    db.query(Endpoint).delete()
    db.query(Instance).delete()
    db.query(Module).delete()
    db.query(Client).delete()
    db.commit()
    print("[OK] Database cleared")


def create_clients(db):
    """Create sample clients"""
    print("\nCreating clients...")
    clients = [
        Client(
            name="Acme Corporation",
            email="admin@acme.corp",
            phone="+1-555-0001",
            timezone="America/New_York",
            is_active=True
        ),
        Client(
            name="TechStart Inc",
            email="ops@techstart.io",
            phone="+1-555-0002",
            timezone="America/Los_Angeles",
            is_active=True
        ),
        Client(
            name="Global Solutions Ltd",
            email="support@globalsolutions.com",
            phone="+44-20-5555-0003",
            timezone="Europe/London",
            is_active=True
        ),
    ]
    
    for client in clients:
        db.add(client)
    db.commit()
    
    print(f"[OK] Created {len(clients)} clients")
    return clients


def create_instances(db, clients):
    """Create instances for each client"""
    print("\nCreating instances...")
    instances = []
    
    environments = ["production", "staging", "development"]
    
    for client in clients:
        for i, env in enumerate(environments[:2]):  # Only prod and staging for each client
            instance = Instance(
                client_id=client.id,
                name=f"{client.name.split()[0]}-{env}",
                host=f"{client.name.lower().replace(' ', '-')}-{env}.example.com",
                environment=env,
                version=f"1.{i}.0",
                is_active=True
            )
            instances.append(instance)
            db.add(instance)
    
    db.commit()
    print(f"[OK] Created {len(instances)} instances")
    return instances


def create_modules(db):
    """Create sample modules"""
    print("\nCreating modules...")
    modules = [
        Module(
            name="API Gateway",
            relative_path="/api",
            description="Main API gateway for external requests",
            category="api",
            version="2.1.0",
            is_public=True
        ),
        Module(
            name="PostgreSQL Database",
            relative_path="/db/postgres",
            description="Primary PostgreSQL database instance",
            category="database",
            version="14.5",
            is_public=False
        ),
        Module(
            name="Redis Cache",
            relative_path="/cache/redis",
            description="Redis caching layer",
            category="cache",
            version="7.0.5",
            is_public=False
        ),
        Module(
            name="RabbitMQ",
            relative_path="/queue/rabbitmq",
            description="Message queue service",
            category="queue",
            version="3.11.2",
            is_public=False
        ),
        Module(
            name="S3 Storage",
            relative_path="/storage/s3",
            description="Object storage service",
            category="storage",
            version="1.0.0",
            is_public=True
        ),
    ]
    
    for module in modules:
        db.add(module)
    db.commit()
    
    print(f"[OK] Created {len(modules)} modules")
    return modules


def create_endpoints(db, modules):
    """Create endpoints for each module"""
    print("\nCreating endpoints...")
    endpoints = []
    
    endpoint_configs = {
        "API Gateway": [
            ("Health Check", "/health", "GET", "health", 500, 5000),
            ("Metrics", "/metrics", "GET", "metrics", 1000, 10000),
            ("Status", "/status", "GET", "status", 500, 5000),
        ],
        "PostgreSQL Database": [
            ("Connection Check", "/check", "GET", "health", 100, 5000),
            ("Query Performance", "/performance", "GET", "metrics", 2000, 30000),
        ],
        "Redis Cache": [
            ("Ping", "/ping", "GET", "health", 50, 1000),
            ("Memory Stats", "/memory", "GET", "metrics", 100, 5000),
        ],
        "RabbitMQ": [
            ("Queue Status", "/queues", "GET", "status", 500, 10000),
            ("Connection Test", "/test", "GET", "health", 200, 5000),
        ],
        "S3 Storage": [
            ("Bucket List", "/buckets", "GET", "status", 1000, 15000),
            ("Health", "/health", "GET", "health", 500, 5000),
        ],
    }
    
    for module in modules:
        if module.name in endpoint_configs:
            for name, path, method, ep_type, exp_time, timeout in endpoint_configs[module.name]:
                endpoint = Endpoint(
                    module_id=module.id,
                    name=name,
                    relative_path=path,
                    method=method,
                    type=ep_type,
                    expected_response_time_ms=exp_time,
                    timeout_ms=timeout
                )
                endpoints.append(endpoint)
                db.add(endpoint)
    
    db.commit()
    print(f"[OK] Created {len(endpoints)} endpoints")
    return endpoints


def create_installations(db, instances, modules):
    """Create installations linking instances and modules"""
    print("\nCreating installations...")
    installations = []
    
    # Each instance gets a subset of modules
    for instance in instances:
        # Production gets all modules
        if "production" in instance.environment:
            modules_to_install = modules
        # Staging gets most modules
        elif "staging" in instance.environment:
            modules_to_install = modules[:4]
        # Development gets basic modules
        else:
            modules_to_install = modules[:2]
        
        for module in modules_to_install:
            installation = Installation(
                module_id=module.id,
                instance_id=instance.id,
                config={
                    "enabled": True,
                    "monitoring_interval": 60,
                    "retry_attempts": 3
                },
                is_active=True
            )
            installations.append(installation)
            db.add(installation)
    
    db.commit()
    print(f"[OK] Created {len(installations)} installations")
    return installations


def create_thresholds(db, installations, endpoints):
    """Create threshold configurations"""
    print("\nCreating thresholds...")
    thresholds = []
    
    for installation in installations:
        # Get endpoints for this installation's module
        module_endpoints = [e for e in endpoints if e.module_id == installation.module_id]
        
        for endpoint in module_endpoints:
            # Response time threshold
            threshold = Threshold(
                installation_id=installation.id,
                endpoint_id=endpoint.id,
                metric_type="response_time",
                warning_min=None,
                warning_max=endpoint.expected_response_time_ms * 1.5,
                error_min=None,
                error_max=endpoint.expected_response_time_ms * 3,
                expected_values={"unit": "milliseconds"},
                is_active=True
            )
            thresholds.append(threshold)
            db.add(threshold)
            
            # Status code threshold for health endpoints
            if endpoint.type == "health":
                threshold = Threshold(
                    installation_id=installation.id,
                    endpoint_id=endpoint.id,
                    metric_type="status_code",
                    warning_min=None,
                    warning_max=None,
                    error_min=None,
                    error_max=None,
                    expected_values={"codes": [200, 204]},
                    is_active=True
                )
                thresholds.append(threshold)
                db.add(threshold)
    
    db.commit()
    print(f"[OK] Created {len(thresholds)} thresholds")
    return thresholds


def create_monitoring_logs(db, installations, endpoints):
    """Create sample monitoring logs"""
    print("\nCreating monitoring logs...")
    logs = []
    
    # Generate logs for the last 24 hours
    now = datetime.utcnow()
    
    for installation in installations[:10]:  # Limit to avoid too many logs
        module_endpoints = [e for e in endpoints if e.module_id == installation.module_id]
        
        for endpoint in module_endpoints:
            # Generate 48 logs (every 30 minutes for 24 hours)
            for i in range(48):
                timestamp = now - timedelta(minutes=30 * i)
                
                # Simulate different scenarios
                if random.random() < 0.85:  # 85% success rate
                    status_code = 200
                    response_time = random.randint(
                        int(endpoint.expected_response_time_ms * 0.5),
                        int(endpoint.expected_response_time_ms * 1.2)
                    )
                    alert_level = "ok"
                    error_message = None
                elif random.random() < 0.5:  # Warning
                    status_code = 200
                    response_time = random.randint(
                        int(endpoint.expected_response_time_ms * 1.5),
                        int(endpoint.expected_response_time_ms * 2.5)
                    )
                    alert_level = "warning"
                    error_message = None
                else:  # Error
                    status_code = random.choice([500, 502, 503, 504])
                    response_time = random.randint(
                        int(endpoint.expected_response_time_ms * 3),
                        endpoint.timeout_ms
                    )
                    alert_level = "error"
                    error_message = f"HTTP {status_code}: Service unavailable"
                
                log = MonitoringLog(
                    installation_id=installation.id,
                    endpoint_id=endpoint.id,
                    response_time_ms=response_time,
                    status_code=status_code,
                    response_body=None,  # Don't store body for mock data
                    error_message=error_message,
                    alert_level=alert_level,
                    alert_triggered=(alert_level != "ok"),
                    extra_data={
                        "region": "us-east-1",
                        "attempt": 1,
                        "protocol": "https"
                    },
                    created_at=timestamp
                )
                logs.append(log)
                db.add(log)
    
    db.commit()
    print(f"[OK] Created {len(logs)} monitoring logs")
    return logs


def main():
    """Main seed function"""
    print("=" * 50)
    print("SEEDING DATABASE WITH NEW MONITORING STRUCTURE")
    print("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_database(db)
        
        # Create data in order
        clients = create_clients(db)
        instances = create_instances(db, clients)
        modules = create_modules(db)
        endpoints = create_endpoints(db, modules)
        installations = create_installations(db, instances, modules)
        thresholds = create_thresholds(db, installations, endpoints)
        logs = create_monitoring_logs(db, installations, endpoints)
        
        print("\n" + "=" * 50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        # Print summary
        print("\nSummary:")
        print(f"  - Clients: {len(clients)}")
        print(f"  - Instances: {len(instances)}")
        print(f"  - Modules: {len(modules)}")
        print(f"  - Endpoints: {len(endpoints)}")
        print(f"  - Installations: {len(installations)}")
        print(f"  - Thresholds: {len(thresholds)}")
        print(f"  - Monitoring Logs: {len(logs)}")
        
    except Exception as e:
        print(f"\n[ERROR] Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()