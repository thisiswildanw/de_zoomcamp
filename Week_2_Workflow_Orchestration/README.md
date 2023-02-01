Week 2 Workflow Orchestration
=============================

> Next Week: (Comming Soon)
> Previous Week: [Introduction]https://github.com/thisiswildanw/de_zoomcamp/tree/master/Week_1_Introduction
> [Back to Start Page](https://github.com/thisiswildanw/de_zoomcamp)

Table of Contents: 
=================
- [Data Lake](#data-lake)
- [Introduction to Workflow Orchestration](#introduction-to-workflow-orchestration)
- [Introduction to Perfect Concepts](#introduction-to-perfect-concepts)
- [ETL with GCP & Perfect](#etl-with-gcp--perfect)
- [From Google Cloud Storage to Big Query](#from-google-cloud-storage-to-big-query)
- [Parameterizing Flow & Deployments with ETL Into GCS Flow](#parameterizing-flow--deployments-with-etl-into-gcs-flow)
- [Schedules & Docker Storage with Infrastructure](#schedules--docker-storage-with-infrastructure) 
- [Perfect Cloud/Additional Resource](#perfect-cloudadditional-resource)


Data Lake
=========

**Data lake** is a central repository that holds big data from many source & type of data (structured, semi-structured & unstructured). The main idea this concept is to ingest data *as quickly as* possible and *make it avalable* for many roles in organization.

Introduction to Workflow Orchestration
======================================

**Workflow orchestration** means gouvering your *data flow* in way that respects orchestration rules and business logic. 

Now what is this **data flow**? 

**Data flow** is what binds and otherwise, *disparate set of application together*. So, workflow orchestration tools is allow you to turn any code into a workflow that can scheduled and observed. 

Here core feature of workflow orchestration:
- Remote execution.
- Scheduling.
- Retries.
- Caching.
- Integrated with external systems (APIs, databases).
- Support ad-hoc runs. 
- Allowing parameterization or alerting when something fails.

Introduction to Perfect Concepts
================================
  
In this lesson, we use [**Prefect**](https:www.prefect.io) as workflow orchestration tool. 

Why **Prefect**?
- It's an *open-source* data flow platform.
- It allow you to add observability and orchestration using *Python* as code. 
- It let us build, run and monitor at scale. 

If you haven't installed **Prefect** yet, follow this [link](https://docs.prefect.io/getting-started/installation/)

<Blockquote>

We recommend this version to install: 
- prefect==2.7.7
- prefect-sqlalchemy==0.2.3
- prefect-gcp[cloud_storage]==0.2.3

</Blockquote>

If you have installed Perfect, Lets try it to orchestrate NYC Taxi Data ingestion flow on[previous](https://github.com/thisiswildanw/de_zoomcamp/tree/master/Week_1_Introduction#ingesting-nyc-taxi-data-to-postgres-with-python) lesson! 



#### 



ETL with GCP & Perfect
======================


From Google Cloud Storage to Big Query 
======================================

Parameterizing Flow & Deployments with ETL into GCS Flow 
========================================================


Schedules & Docker Storage with Infrastructure
===============================================

Perfect Cloud/Additional Resource
=================================