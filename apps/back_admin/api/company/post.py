from fastapi import APIRouter

from back_admin.database import database
from back_admin.models import CompanyModel
from sqlalchemy import select, update

router = APIRouter(prefix="/company", tags=["company-admin"])


async def exe_q(q, return_scalar=False):
    async with database.session() as session:
        temp = await session.execute(q)
        return temp.scalar() if return_scalar else temp.scalars().all()


@router.post("")
async def getCompanies():
    stmt = select(CompanyModel)
    companies = await exe_q(stmt)

    return {
        "status": "OK",
        "companies": companies,
    }


@router.put("/edit")
async def editCompany(company_name: str, company_id: int):
    company_stmt = update(
        CompanyModel,
    ).where(
        CompanyModel.id == company_id,
    ).values(
        name=company_name,
    )

    async with database.session() as session:
        company_to_change = await session.execute(company_stmt)

    return {
        "status": "OK",
        "company": company_to_change,
    }


@router.post("/add")
async def addCompany(company_name: str):
    new_company = CompanyModel(
        name=company_name,
    )
    async with database.session() as session:
        session.add(new_company)
        session.commit()

    return {
        "status": "OK",
        "new_company": new_company,
    }


@router.delete("/delete")
async def deleteCompany(company_id: int):
    company_delete_stmt = select(
        CompanyModel,
    ).where(
        CompanyModel.id == company_id,
    )
    async with database.session() as session:
        await session.delete(company_delete_stmt)
        session.commit()

    return {
        "status": "OK",
        "company_id": company_id,
    }
