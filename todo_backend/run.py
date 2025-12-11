from app import app

if __name__ == "__main__":
    # Bind explicitly to host and port for the preview runner/environment
    app.run(host="0.0.0.0", port=3001)
