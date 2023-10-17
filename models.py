from tortoise import Model, fields
from pydantic import BaseModel
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

class User(Model):
    id = fields.IntField(pk=True, index = True)
    user_name = fields.CharField(max_length=20, null = False, unique = True)
    email = fields.CharField(max_length=200, null = False, unique = True)
    password = fields.CharField(max_length=100, null = False)
    is_verified = fields.BooleanField(default=False)
    join_date  = fields.DateField(default=datetime.utcnow)


class Business(Model):
    id = fields.IntField(pk=True, index = True)
    Business_name = fields.CharField(max_length=20, null = False, unique = True)
    city = fields.CharField(max_length=100, null = False, default="unspecified")
    region = fields.CharField(max_length=100, null = False, default="unspecified")
    Business_description = fields.TextField(null = False)
    logo = fields.CharField(max_length=200, null = False, default = "default.png")
    owner = fields.ForeignKeyField("models.User", related_name="businesses")

class product(Model):
    id = fields.IntField(pk=True, index = True)
    name = fields.CharField(max_length=100, null = False, index = True)
    category = fields.CharField(max_length=30, index = True)
    original_price = fields.DecimalField(max_digits=12, decimal_places=2, null = False)
    new_price = fields.DecimalField(max_digits=12, decimal_places=2, null = False)
    percentage_discount = fields.IntField()
    offer_expiration_date = fields.DateField(default=datetime.utcnow)
    product_image = fields.CharField(max_length=200, null = False, default = "productDefault.png")
    Business = fields.ForeignKeyField("models.Business", related_name="products")

user_pydatic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
user_pydaticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
user_pydaticOut = pydantic_model_creator(User, name="UserOut", exclude=("password",))

Business_pydatic = pydantic_model_creator(Business, name="Business")
Business_pydaticIn = pydantic_model_creator(Business, name="BusinessIn", exclude_readonly=True)

product_pydatic = pydantic_model_creator(product, name="Product")
product_pydaticIn = pydantic_model_creator(product, name="ProductIn", exclude=("percentage_discount",))