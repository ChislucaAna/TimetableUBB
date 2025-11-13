# UBB Timetable API

This is a simple API that allows you to get the timetables for all groups at UBB Cluj-Napoca Computer Science faculty.

## Usage

```bash
docker build -t ubb-timetable-api .
docker run -p 8000:8000 ubb-timetable-api
```

## Endpoints

### Get all timetables

```bash
http://localhost:8000/
```

### Get all schedules

```bash
http://localhost:8000/schedules
```

### Get schedule for a specific group

```bash
http://localhost:8000/schedule?group=1011
```

## Swagger UI

```bash
http://localhost:8000/swagger
```

## Redoc UI

```bash
http://localhost:8000/redoc
```