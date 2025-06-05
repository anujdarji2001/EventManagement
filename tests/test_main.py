import pytest
from httpx import AsyncClient
from datetime import datetime
import pytz

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_create_event():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/events/", json={
            "name": "Test Event",
            "location": "Test City",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 2
        })
        assert response.status_code == 201
        assert response.json()["name"] == "Test Event"

@pytest.mark.asyncio
async def test_create_event_with_timezone():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/events/", json={
            "name": "NYC Event",
            "location": "New York",
            "start_time": "2024-06-01T10:00:00-04:00",  # EDT time
            "end_time": "2024-06-01T12:00:00-04:00",    # EDT time
            "max_capacity": 2
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "NYC Event"
        # Verify times are stored with timezone info
        assert "T" in data["start_time"]
        assert "T" in data["end_time"]

@pytest.mark.asyncio
async def test_list_events_with_timezone():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create an event in IST
        await ac.post("/events/", json={
            "name": "IST Event",
            "location": "Mumbai",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 2
        })
        
        # List events with different timezone
        response = await ac.get("/events/?timezone=America/New_York")
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) > 0
        
        # Verify times are converted to New York timezone
        event = data["events"][0]
        start_time = datetime.fromisoformat(event["start_time"].replace('Z', '+00:00'))
        # Check if the timezone offset matches New York's offset
        ny_tz = pytz.timezone('America/New_York')
        # Create a naive datetime and localize it to get the offset
        naive_dt = datetime(2024, 6, 1, 10, 0)  # Use a fixed date for consistent testing
        ny_dt = ny_tz.localize(naive_dt)
        assert start_time.utcoffset() == ny_dt.utcoffset()

@pytest.mark.asyncio
async def test_list_events_invalid_timezone():
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get("/events/?timezone=Invalid/Timezone")
        assert response.status_code == 422
        assert "Invalid timezone" in response.json()["detail"]

@pytest.mark.asyncio
async def test_timezone_conversion_accuracy():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create event in IST
        ist_time = "2024-06-01T10:00:00+05:30"
        await ac.post("/events/", json={
            "name": "Time Test Event",
            "location": "Test Location",
            "start_time": ist_time,
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 2
        })
        
        # Get in different timezones and verify conversion
        timezones = {
            'America/New_York': '-04:00',  # EDT
            'Asia/Tokyo': '+09:00',
            'Europe/London': '+01:00'      # BST
        }
        
        for tz, offset in timezones.items():
            response = await ac.get(f"/events/?timezone={tz}")
            assert response.status_code == 200
            event = response.json()["events"][0]
            start_time = event["start_time"]
            assert offset in start_time  # Verify correct timezone offset

@pytest.mark.asyncio
async def test_timezone_preservation():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create event with specific timezone
        original_time = "2024-06-01T10:00:00-07:00"  # PDT
        response = await ac.post("/events/", json={
            "name": "PDT Event",
            "location": "Los Angeles",
            "start_time": original_time,
            "end_time": "2024-06-01T12:00:00-07:00",
            "max_capacity": 2
        })
        assert response.status_code == 201
        
        # Get in original timezone
        response = await ac.get("/events/?timezone=America/Los_Angeles")
        assert response.status_code == 200
        event = response.json()["events"][0]
        assert "-07:00" in event["start_time"]  # Verify original timezone preserved

@pytest.mark.asyncio
async def test_list_events_pagination():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create 15 events
        for i in range(15):
            await ac.post("/events/", json={
                "name": f"Event {i}",
                "location": f"Loc {i}",
                "start_time": "2024-06-01T10:00:00+05:30",
                "end_time": "2024-06-01T12:00:00+05:30",
                "max_capacity": 10
            })
        # Get first page, size 5
        resp = await ac.get("/events/?page=1&size=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data and "page" in data and "size" in data and "events" in data
        assert data["page"] == 1
        assert data["size"] == 5
        assert isinstance(data["events"], list)
        assert len(data["events"]) == 5
        total = data["total"]
        # Get third page, size 5
        resp2 = await ac.get("/events/?page=3&size=5")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["page"] == 3
        assert data2["size"] == 5
        assert isinstance(data2["events"], list)
        # Should have 5 events on page 3 if 15+ events exist, or fewer if not
        assert len(data2["events"]) <= 5
        # Get page beyond available
        page = 10
        size = 5
        resp3 = await ac.get(f"/events/?page={page}&size={size}")
        assert resp3.status_code == 200
        data3 = resp3.json()
        start = (page - 1) * size
        if start >= total:
            assert data3["events"] == []
        else:
            expected_count = max(0, min(size, total - start))
            assert len(data3["events"]) == expected_count

@pytest.mark.asyncio
async def test_register_attendee():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create event first
        event_resp = await ac.post("/events/", json={
            "name": "Reg Event",
            "location": "Reg City",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 1
        })
        event_id = event_resp.json()["id"]
        # Register attendee
        reg_resp = await ac.post(f"/events/{event_id}/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        assert reg_resp.status_code == 201
        # Try duplicate registration
        dup_resp = await ac.post(f"/events/{event_id}/register", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        assert dup_resp.status_code == 400

@pytest.mark.asyncio
async def test_overbooking():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create event with capacity 1
        event_resp = await ac.post("/events/", json={
            "name": "Overbook Event",
            "location": "Over City",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 1
        })
        event_id = event_resp.json()["id"]
        # Register first attendee
        await ac.post(f"/events/{event_id}/register", json={
            "name": "Bob",
            "email": "bob@example.com"
        })
        # Register second attendee (should fail)
        resp = await ac.post(f"/events/{event_id}/register", json={
            "name": "Charlie",
            "email": "charlie@example.com"
        })
        assert resp.status_code == 400
        assert "fully booked" in resp.json()["detail"].lower()

@pytest.mark.asyncio
async def test_register_to_nonexistent_event():
    async with AsyncClient(base_url=BASE_URL) as ac:
        resp = await ac.post(f"/events/999999/register", json={
            "name": "Ghost",
            "email": "ghost@example.com"
        })
        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_list_attendees_for_nonexistent_event():
    async with AsyncClient(base_url=BASE_URL) as ac:
        resp = await ac.get(f"/events/999999/attendees")
        assert resp.status_code == 404

@pytest.mark.asyncio
async def test_list_attendees():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Create event
        event_resp = await ac.post("/events/", json={
            "name": "List Event",
            "location": "List City",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 5
        })
        event_id = event_resp.json()["id"]
        # Register attendees
        for i in range(3):
            await ac.post(f"/events/{event_id}/register", json={
                "name": f"User{i}",
                "email": f"user{i}@example.com"
            })
        # List attendees
        resp = await ac.get(f"/events/{event_id}/attendees?page=1&size=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["attendees"]) == 2
        # Pagination edge case: page beyond available
        resp2 = await ac.get(f"/events/{event_id}/attendees?page=10&size=2")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["attendees"] == []

@pytest.mark.asyncio
async def test_event_input_validation():
    async with AsyncClient(base_url=BASE_URL) as ac:
        # Missing name
        resp = await ac.post("/events/", json={
            "location": "City",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 10
        })
        assert resp.status_code == 422
        # Invalid email
        event_resp = await ac.post("/events/", json={
            "name": "Valid Event",
            "location": "City",
            "start_time": "2024-06-01T10:00:00+05:30",
            "end_time": "2024-06-01T12:00:00+05:30",
            "max_capacity": 10
        })
        event_id = event_resp.json()["id"]
        resp2 = await ac.post(f"/events/{event_id}/register", json={
            "name": "Invalid Email",
            "email": "not-an-email"
        })
        assert resp2.status_code == 422
