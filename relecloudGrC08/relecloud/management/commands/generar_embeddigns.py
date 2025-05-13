from django.core.management.base import BaseCommand
from relecloud.models import Pueblo
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

class Command(BaseCommand):
    help = 'Genera el índice FAISS con información de Pueblo, Comunidad y Reviews'

    def handle(self, *args, **kwargs):
        modelo = SentenceTransformer("all-MiniLM-L6-v2")
        textos, ids = [], []

        pueblos = Pueblo.objects.select_related('comunidad').prefetch_related('reviews')

        for pueblo in pueblos:
            comunidad_nombre = pueblo.comunidad.nombre if pueblo.comunidad else ""
            valoracion_media = pueblo.calculate_popularity()

            comentarios = [review.comment for review in pueblo.reviews.all() if review.comment]
            comentarios_texto = " ".join(comentarios[:3])  # máximo 3 comentarios

            texto = f"""
            Nombre: {pueblo.name}
            Comunidad: {comunidad_nombre}
            Ubicación: {pueblo.ubicacion}
            Habitantes: {pueblo.habitantes}
            Descripción: {pueblo.descripcion}
            Servicios: {pueblo.servicios}
            Actividades: {pueblo.actividades}
            Incentivos: {pueblo.incentivos}
            Valoración media: {valoracion_media:.1f}
            Comentarios destacados: {comentarios_texto}
            """

            textos.append(texto)
            ids.append(pueblo.id)

        vectores = modelo.encode(textos)
        index = faiss.IndexFlatL2(384)
        index.add(np.array(vectores))

        faiss.write_index(index, "relecloud/faiss_index.index")
        with open("relecloud/id_map.pkl", "wb") as f:
            pickle.dump(ids, f)

        self.stdout.write(self.style.SUCCESS("✅ Embeddings generados con Pueblo + Comunidad + Reviews."))
