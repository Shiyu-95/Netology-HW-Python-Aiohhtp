import json
from aiohttp import web
from models import init_orm, close_orm, Session, Advertisement
from sqlalchemy.exc import IntegrityError

def get_http_error(err_cls, message: str | dict | list):
    error_msg = json.dumps({"error": message})
    return err_cls(
        text=error_msg,
        content_type='application/json'
    )

app = web.Application()

async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    print("FINISH")
    await close_orm()

@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)

async def add_advertisement(advertisement: Advertisement, session: Session):
    session.add(advertisement)
    try:
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "Advertisement already exists")

class AdvertisementView(web.View):
    @property
    def adv_id(self):
        return int(self.request.match_info["adv_id"])

    @property
    def session(self):
        return self.request.session

    async def get_advertisement(self):
        advertisement = await self.session.get(Advertisement, self.adv_id)
        if advertisement is None:
            raise get_http_error(web.HTTPNotFound, "Advertisement not found")
        return advertisement

    async def get(self):
        advertisement = await self.get_advertisement()
        return web.json_response(advertisement.dict)

    async def post(self):
        json_data = await self.request.json()
        advertisement = Advertisement(
            title=json_data["title"],
            description=json_data["description"],
            owner=json_data["owner"]
        )
        await add_advertisement(advertisement, self.session)
        return web.json_response(advertisement.id_dict)

    async def patch(self):
        json_data = await self.request.json()
        advertisement = await self.get_advertisement()
        if "title" in json_data:
            advertisement.title = json_data["title"]
        if "description" in json_data:
            advertisement.description = json_data["description"]
        await self.session.commit()
        return web.json_response(advertisement.id_dict)

    async def delete(self):
        advertisement = await self.get_advertisement()
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"message": "Advertisement deleted"})

app.add_routes([
    web.post("/api/v1/advertisements", AdvertisementView),
    web.get("/api/v1/advertisements/{adv_id:\d+}", AdvertisementView),
    web.patch("/api/v1/advertisements/{adv_id:\d+}", AdvertisementView),
    web.delete("/api/v1/advertisements/{adv_id:\d+}", AdvertisementView)
])

web.run_app(app)