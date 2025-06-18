import uvicorn
import os

if __name__ == "__main__":
    # Asegúrate de que el directorio actual es donde está el script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.") 