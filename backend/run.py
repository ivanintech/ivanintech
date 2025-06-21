import uvicorn
import os

if __name__ == "__main__":
    # Asegúrate de que el directorio actual es donde está el script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Render proporciona el puerto a través de la variable de entorno PORT
    # Usamos 8000 como fallback para el desarrollo local
    port = int(os.environ.get("PORT", 8000))

    try:
        uvicorn.run(
            "app.main:app", 
            host="0.0.0.0", 
            port=port, 
            reload=False
        )
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.") 