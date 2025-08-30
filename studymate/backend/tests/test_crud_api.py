import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.session import get_db
from app.db.models import User, Document, Chat
from app.core.auth import get_password_hash


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_superuser(db_session: AsyncSession):
    """Create a test superuser."""
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        is_active=True,
        is_superuser=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_document(db_session: AsyncSession):
    """Create a test document."""
    document = Document(
        filename="test.pdf",
        s3_key="test/test.pdf",
        status="ready"
    )
    db_session.add(document)
    await db_session.commit()
    await db_session.refresh(document)
    return document


@pytest.fixture
async def test_chat(db_session: AsyncSession, test_user: User):
    """Create a test chat."""
    chat = Chat(
        title="Test Chat",
        user_id=test_user.id
    )
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)
    return chat


class TestAuthentication:
    """Test authentication endpoints."""
    
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post("/auth/register", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_duplicate_username(self, client: AsyncClient, test_user: User):
        """Test registration with duplicate username."""
        response = await client.post("/auth/register", json={
            "username": test_user.username,
            "email": "different@example.com",
            "password": "password123"
        })
        assert response.status_code == 400
        assert "username already exists" in response.json()["detail"]

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with duplicate email."""
        response = await client.post("/auth/register", json={
            "username": "differentuser",
            "email": test_user.email,
            "password": "password123"
        })
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"]

    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post("/auth/login-json", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    async def test_get_current_user(self, client: AsyncClient, test_user: User):
        """Test getting current user with valid token."""
        # First login to get token
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Use token to get current user
        response = await client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email


class TestDocumentCRUD:
    """Test document CRUD operations."""
    
    async def test_create_document(self, client: AsyncClient, test_user: User):
        """Test creating a document."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Create document
        response = await client.post("/crud/documents", 
            json={
                "filename": "new_document.pdf",
                "s3_key": "uploads/new_document.pdf",
                "status": "processing"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "new_document.pdf"
        assert data["status"] == "processing"

    async def test_get_documents(self, client: AsyncClient, test_user: User, test_document: Document):
        """Test getting documents list."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Get documents
        response = await client.get("/crud/documents", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    async def test_get_document_by_id(self, client: AsyncClient, test_user: User, test_document: Document):
        """Test getting a specific document."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Get document
        response = await client.get(f"/crud/documents/{test_document.id}", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_document.id)
        assert data["filename"] == test_document.filename

    async def test_update_document(self, client: AsyncClient, test_user: User, test_document: Document):
        """Test updating a document."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Update document
        response = await client.put(f"/crud/documents/{test_document.id}", 
            json={"status": "ready"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    async def test_delete_document(self, client: AsyncClient, test_user: User, test_document: Document):
        """Test deleting a document."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Delete document
        response = await client.delete(f"/crud/documents/{test_document.id}", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204


class TestChatCRUD:
    """Test chat CRUD operations."""
    
    async def test_create_chat(self, client: AsyncClient, test_user: User):
        """Test creating a chat."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Create chat
        response = await client.post("/crud/chats", 
            json={"title": "New Chat"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Chat"
        assert data["user_id"] == str(test_user.id)

    async def test_get_user_chats(self, client: AsyncClient, test_user: User, test_chat: Chat):
        """Test getting chats for current user."""
        # Login first
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Get chats
        response = await client.get("/crud/chats", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        # Verify all chats belong to the current user
        for chat in data["items"]:
            assert chat["user_id"] == str(test_user.id)


class TestUserManagement:
    """Test user management (superuser only)."""
    
    async def test_get_users_superuser(self, client: AsyncClient, test_superuser: User):
        """Test getting users list as superuser."""
        # Login as superuser
        login_response = await client.post("/auth/login-json", json={
            "username": test_superuser.username,
            "password": "adminpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Get users
        response = await client.get("/crud/users", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_users_regular_user(self, client: AsyncClient, test_user: User):
        """Test getting users list as regular user (should fail)."""
        # Login as regular user
        login_response = await client.post("/auth/login-json", json={
            "username": test_user.username,
            "password": "testpassword123"
        })
        token = login_response.json()["access_token"]
        
        # Try to get users (should fail)
        response = await client.get("/crud/users", 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403
