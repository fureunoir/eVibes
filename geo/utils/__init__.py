from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from graphene.types.scalars import Scalar
from graphene_django.converter import convert_django_field
from graphql.language import ast


class PointScalar(Scalar):
    """Custom scalar for GeoDjango PointField"""

    @staticmethod
    def serialize(point):
        if not isinstance(point, Point):
            raise Exception("Expected a Point instance")
        return {"x": point.x, "y": point.y}

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.ObjectValue):
            return Point(x=node.value["x"], y=node.value["y"])
        return None

    @staticmethod
    def parse_value(value):
        if isinstance(value, dict):
            return Point(x=value["x"], y=value["y"])
        return None


@convert_django_field.register(PointField)
def convert_point_field_to_custom_type(field, registry=None):
    return PointScalar(description=field.help_text, required=not field.null)
