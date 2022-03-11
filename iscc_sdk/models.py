"""*Extendes IsccMeta schema model*."""
from typing import Optional
from pydantic import Field
from iscc_schema import IsccMeta as BaseIsccMeta
import iscc_core as ic


__all__ = [
    "IsccMeta",
]


class IsccMeta(BaseIsccMeta):
    class Config:
        extra = "forbid"
        validate_assignment = True
        use_enum_values = True

    def dict(self, *args, exclude_none=True, exclude_unset=True, by_alias=True, **kwargs):
        """
        Overide defaults to exclude none and unset values and translate aliases.

        !!! note
            This overides the default BaseModel.dict()
        """
        return super().dict(
            *args,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset,
            by_alias=by_alias,
            **kwargs,
        )

    def json(self, *args, exclude_none=True, by_alias=True, **kwargs):
        """
        Overide defaults to exclude empty fields and use aliases.

        The by_alias=True allows us to generate valid JSON-LD by default. It translates
        our python "_context" property to @context

        !!! note
            This overides the default BaseModel.json()
        """
        return super().json(
            *args,
            exclude_none=exclude_none,
            by_alias=by_alias,
            **kwargs,
        )

    def json_ld(self):
        # type: () -> bytes
        """Include default context, schema, type and create coanonical json data."""
        return ic.json_canonical(self.dict(exclude_unset=False))

    @property
    def iscc_obj(self):
        # type: () -> ic.Code
        """ISCC Code object."""
        return ic.Code(self.iscc)
