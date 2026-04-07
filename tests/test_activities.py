"""Comprehensive FastAPI tests for High School Management System API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test state using fixtures (client, mock_activities)
- Act: Call the endpoint
- Assert: Verify response status, data structure, and correctness
"""

import pytest


class TestGetActivities:
    """Unit tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Fresh client with mock activities fixture
        Act: GET /activities
        Assert: 200 OK with all activities
        """
        # Arrange (implicit via client fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Soccer Team" in activities

    def test_get_activities_returns_activity_structure(self, client):
        """
        Arrange: Fresh client with mock activities
        Act: GET /activities
        Assert: Each activity has required fields
        """
        # Arrange (implicit via client fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_participant_data(self, client):
        """
        Arrange: Fresh client with activities containing participants
        Act: GET /activities
        Assert: Participants list is returned correctly
        """
        # Arrange (implicit via client fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert activities["Chess Club"]["participants"] == ["alice@example.com"]
        assert activities["Soccer Team"]["participants"] == []


class TestSignupForActivity:
    """Unit tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Fresh client, target activity (Soccer Team), new student email
        Act: POST signup request
        Assert: 200 OK with success message
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "newstudent@example.com"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_adds_participant_to_activity(self, client, mock_activities):
        """
        Arrange: Fresh client, empty activity (Soccer Team has 0 participants)
        Act: POST signup request
        Assert: Participant count increases and student is in list
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "newstudent@example.com"
        initial_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert email in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_activity_not_found(self, client):
        """
        Arrange: Fresh client, non-existent activity name
        Act: POST signup to non-existent activity
        Assert: 404 Not Found
        """
        # Arrange
        activity_name = "NonExistentClub"
        email = "student@example.com"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_signed_up(self, client):
        """
        Arrange: Fresh client, student already in Chess Club
        Act: POST signup for same activity twice
        Assert: First succeeds (200), second fails (400)
        """
        # Arrange
        activity_name = "Chess Club"
        email = "alice@example.com"  # Already in Chess Club
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up for this activity"

    def test_signup_multiple_students_different_activities(self, client):
        """
        Arrange: Fresh client
        Act: Sign up multiple students to different activities
        Assert: All signups succeed
        """
        # Arrange
        signups = [
            ("Chess Club", "charlie@example.com"),
            ("Programming Class", "diana@example.com"),
            ("Soccer Team", "evan@example.com"),
        ]
        
        # Act & Assert
        for activity_name, email in signups:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200


class TestRemoveParticipant:
    """Unit tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_delete_participant_success(self, client, mock_activities):
        """
        Arrange: Fresh client, Chess Club has alice@example.com
        Act: DELETE alice from Chess Club
        Assert: 200 OK and alice is removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        email = "alice@example.com"
        assert email in mock_activities[activity_name]["participants"]
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in mock_activities[activity_name]["participants"]

    def test_delete_participant_activity_not_found(self, client):
        """
        Arrange: Fresh client, non-existent activity
        Act: DELETE from non-existent activity
        Assert: 404 Not Found
        """
        # Arrange
        activity_name = "NonExistentClub"
        email = "student@example.com"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_delete_participant_not_found(self, client):
        """
        Arrange: Fresh client, activity exists but student is not in it
        Act: DELETE student not in activity
        Assert: 404 Not Found
        """
        # Arrange
        activity_name = "Soccer Team"  # Has no participants
        email = "notamember@example.com"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"


class TestIntegrationWorkflows:
    """Integration tests for multi-step workflows."""

    def test_signup_then_verify_participant_in_get_activities(self, client, mock_activities):
        """
        Arrange: Fresh client, Soccer Team initially empty
        Act: 1) POST signup 2) GET activities
        Assert: Participant appears in GET response
        """
        # Arrange
        activity_name = "Soccer Team"
        email = "newcoach@example.com"
        
        # Act - Step 1: Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Act - Step 2: Get activities and verify
        get_response = client.get("/activities")
        
        # Assert
        assert get_response.status_code == 200
        activities = get_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_then_delete_one_verify_state(self, client, mock_activities):
        """
        Arrange: Fresh client, Soccer Team empty
        Act: 1) Sign up student1 2) Sign up student2 3) DELETE student1 4) GET activities
        Assert: Only student2 remains in participants
        """
        # Arrange
        activity_name = "Soccer Team"
        student1 = "player1@example.com"
        student2 = "player2@example.com"
        
        # Act - Step 1: Sign up student1
        response1 = client.post(f"/activities/{activity_name}/signup?email={student1}")
        assert response1.status_code == 200
        
        # Act - Step 2: Sign up student2
        response2 = client.post(f"/activities/{activity_name}/signup?email={student2}")
        assert response2.status_code == 200
        
        # Act - Step 3: Delete student1
        delete_response = client.delete(f"/activities/{activity_name}/participants?email={student1}")
        assert delete_response.status_code == 200
        
        # Act - Step 4: Verify final state
        get_response = client.get("/activities")
        
        # Assert
        activities = get_response.json()
        participants = activities[activity_name]["participants"]
        assert student1 not in participants
        assert student2 in participants
        assert len(participants) == 1

    def test_signup_delete_then_signup_again(self, client, mock_activities):
        """
        Arrange: Fresh client
        Act: 1) Sign up 2) Delete 3) Sign up again
        Assert: All steps succeed and final state shows participant
        """
        # Arrange
        activity_name = "Chess Club"
        email = "transferstudent@example.com"
        
        # Act - Step 1: Sign up
        signup1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup1.status_code == 200
        
        # Act - Step 2: Delete
        delete = client.delete(f"/activities/{activity_name}/participants?email={email}")
        assert delete.status_code == 200
        assert email not in mock_activities[activity_name]["participants"]
        
        # Act - Step 3: Sign up again (should succeed now)
        signup2 = client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert signup2.status_code == 200
        assert email in mock_activities[activity_name]["participants"]
