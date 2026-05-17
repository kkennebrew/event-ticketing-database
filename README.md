# Event Ticketing Database — PostgreSQL Design & Implementation

A relational database designed and implemented in PostgreSQL to manage event bookings, spectator records, and ticket cancellations for a live events ticketing system.

## Overview

This project covers the full database development lifecycle: entity-relationship modelling, schema design, SQL implementation, and Python integration. The schema enforces business rules through constraints, views, triggers, and stored functions — including automatic overbooking prevention and cancellation logging.

## Features implemented

- **ERD design** — entity-relationship diagram modelling four core entities: Event, Spectator, Ticket, Cancel
- **Schema** — normalised relational schema with primary keys, foreign keys, and referential integrity constraints
- **Views** — `v_event_bookings` aggregates live ticket counts and remaining capacity per event
- **Functions** — `fn_ticket_count()` returns valid (non-cancelled) ticket count for any event
- **Triggers** — capacity enforcement trigger prevents overbooking on insert; deletion trigger automatically logs cancelled tickets to the Cancel table
- **Python integration** — psycopg2 scripts connect to and query the live PostgreSQL database

## Tools and technologies

| Tool | Purpose |
|---|---|
| PostgreSQL | Relational database engine |
| SQL (DDL/DML) | Schema creation, data insertion, views, triggers, functions |
| Python / psycopg2 | Database connectivity and query execution |
| Visual Paradigm | ERD design |

## Files

| File | Description |
|---|---|
| `ERD Assessment_1.png` | Entity-relationship diagram |
| `schema.sql` | Full DDL — tables, views, functions, triggers, and test data |
| `Part3.py` | Python script for PostgreSQL interaction |
| `python_postgresql_notes.txt` | Notes on Python–PostgreSQL connection setup |

## Running the schema

```bash
# In psql
\i schema.sql
```

```bash
# Python setup
pip install psycopg2-binary
python Part3.py
```

---
*Database Management module — Assessment 1, 2025–26.*
