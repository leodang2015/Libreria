from fastapi import APIRouter, Query, status

from ..controllers import prestamos as controlador
from ..core.dependencies import SessionDep
from ..schemas.prestamo import PrestamoActualizar, PrestamoCrear, PrestamoLeer

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


@router.get("", response_model=list[PrestamoLeer])
def listar_prestamos(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return controlador.listar(db, skip=skip, limit=limit)


@router.get("/{prestamo_id}", response_model=PrestamoLeer)
def obtener_prestamo(prestamo_id: int, db: SessionDep):
    return controlador.obtener(db, prestamo_id)


@router.post("", response_model=PrestamoLeer, status_code=status.HTTP_201_CREATED)
def crear_prestamo(datos: PrestamoCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{prestamo_id}", response_model=PrestamoLeer)
def actualizar_prestamo(prestamo_id: int, datos: PrestamoActualizar, db: SessionDep):
    return controlador.actualizar(db, prestamo_id, datos)


@router.delete("/{prestamo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_prestamo(prestamo_id: int, db: SessionDep):
    controlador.eliminar(db, prestamo_id)
    return None
