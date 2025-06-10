# init.sh
mkdir -p app/{alembic/{versions},api,config,core,database/{models,repositories},pipelines/{anomaly_detection,change_analysis,monitoring},services,tasks,utils}
mkdir -p {data,docker,playground,requests/jobs,tests/{test_pipelines,test_services,test_utils}}
touch app/alembic/{env.py,script.py.mako}
touch app/alembic.ini
touch app/api/{__init__.py,dependencies.py,endpoints.py,job_schema.py,router.py}
touch app/config/{__init__.py,celery_config.py,database_config.py,settings.py}
touch app/core/{__init__.py,base.py,pipeline.py,router.py,schema.py,task.py,validate.py}
touch app/database/{__init__.py,base_repository.py,connection.py,repository_factory.py}
touch app/database/models/{__init__.py,job.py,satellite_data.py,alert.py,anomaly.py}
touch app/database/repositories/{job_repository.py,job_run_repository.py,satellite_data_repository.py,alert_repository.py,anomaly_repository.py}
touch app/pipelines/{__init__.py,registry.py}
touch app/pipelines/anomaly_detection/{__init__.py,pipeline.py,data_fetch.py,preprocessing.py,anomaly_analysis.py,alert_routing.py,data_storage.py,notification.py}
touch app/pipelines/change_analysis/{__init__.py,pipeline.py,change_detection.py,temporal_comparison.py}
touch app/pipelines/monitoring/{__init__.py,pipeline.py,data_validation.py,health_check.py}
touch app/services/{__init__.py,db_service.py,earth_engine_service.py,satellite_data_service.py,processing_service.py,anomaly_detector.py,alerting_service.py,notification_service.py,scheduler_service.py,geospatial_utils.py,utils.py}
touch app/tasks/{__init__.py,tasks.py,job_processor.py,periodic_tasks.py,simple_task.py}
touch app/utils/{__init__.py,cache.py,date_utils.py,decorators.py,exceptions.py,geometry.py,logging.py,validators.py,visualization.py}
touch app/{main.py,requirements.txt,start.sh,makemigration.sh,migrate.sh}
touch data/{anomaly_thresholds.json,sample_polygons.json,test_coordinates.json}
touch docker/{Caddyfile,docker-compose.yml,Dockerfile.api,Dockerfile.celery,logs.sh,start.sh}
touch docker-compose.yml
touch playground/{data_processing_playground.py,earth_engine_playground.py,pipeline_playground.py,visualization_playground.py}
touch requests/jobs/{anomaly_detection_job.json,batch_processing_job.json,change_analysis_job.json,periodic_monitoring_job.json}
touch requests/send_job.py
touch tests/{__init__.py}
touch tests/test_pipelines/{test_anomaly_detection.py,test_change_analysis.py,test_monitoring.py}
touch tests/test_services/{test_alerting.py,test_earth_engine.py,test_processing.py}
touch tests/test_utils/{test_geospatial_utils.py,test_validators.py}
touch {README.md,pyrightconfig.json}


# install.sh
pip install "fastapi[standard]" sqlalchemy celery redis pydantic pydantic-settings python-dateutil alembic psycopg2-binary python-dotenv

# detect process and kill it
lsof -i :8000
kill -9 12345

