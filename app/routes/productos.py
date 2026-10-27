from fastapi import APIRouter, Query, Response, status

from ..controllers import productos as controlador
from ..core.dependencies import SessionDep
from ..schemas.producto import ProductoActualizar, ProductoCrear, ProductoLeer

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("", response_model=list[ProductoLeer])
def listar_productos(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    categoria_id: int | None = Query(None, gt=0),
    buscar: str | None = Query(None, description="Texto contenido en el nombre"),
    solo_activos: bool = False,
):
    return controlador.listar(db, skip, limit, categoria_id, buscar, solo_activos)


@router.get("/{producto_id}", response_model=ProductoLeer)
def obtener_producto(producto_id: int, db: SessionDep):
    return controlador.obtener(db, producto_id)


@router.post("", response_model=ProductoLeer, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{producto_id}", response_model=ProductoLeer)
def actualizar_producto(producto_id: int, datos: ProductoActualizar, db: SessionDep):
    return controlador.actualizar(db, producto_id, datos)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, db: SessionDep) -> Response:
    controlador.eliminar(db, producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
