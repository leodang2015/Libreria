from fastapi import APIRouter, Query, status

from ..controllers import socios as controlador
from ..core.dependencies import SessionDep
from ..schemas.socio import SocioActualizar, SocioCrear, SocioLeer

router = APIRouter(prefix="/socios", tags=["Socios"])


@router.get("", response_model=list[SocioLeer])
def listar_socios(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    return controlador.listar(db, skip=skip, limit=limit)


@router.get("/{socio_id}", response_model=SocioLeer)
def obtener_socio(socio_id: int, db: SessionDep):
    return controlador.obtener(db, socio_id)


@router.post("", response_model=SocioLeer, status_code=status.HTTP_201_CREATED)
def crear_socio(datos: SocioCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{socio_id}", response_model=SocioLeer)
def actualizar_socio(socio_id: int, datos: SocioActualizar, db: SessionDep):
    return controlador.actualizar(db, socio_id, datos)


@router.delete("/{socio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_socio(socio_id: int, db: SessionDep):
    controlador.eliminar(db, socio_id)
    return None
