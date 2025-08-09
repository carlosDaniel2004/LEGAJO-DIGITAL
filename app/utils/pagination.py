# Importa la librería math para la operación de techo (ceiling).
import math

# Define una clase simple para manejar la lógica de la paginación.
class SimplePagination:
    # El constructor recibe los resultados de la consulta, la página actual, items por página y el total de registros.
    def __init__(self, query_result, page, per_page, total):
        self.items = query_result
        self.page = page
        self.per_page = per_page
        self.total = total

    # Calcula el número total de páginas.
    @property
    def pages(self):
        if self.per_page == 0:
            return 0
        return math.ceil(self.total / self.per_page)

    # Propiedades para verificar si hay página anterior o siguiente.
    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    # Propiedades para obtener el número de la página anterior o siguiente.
    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None

    # Genera los números de página para mostrar en la interfaz (ej: 1, 2, ..., 5, 6, 7, ..., 10).
    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num