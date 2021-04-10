from django.db.models import (
    Model,
)

from apps.shop.exceptions import (
    NonPositiveCountException,
)


class DeltaUtil:
    @staticmethod
    def smart_delta(model: Model,
                    identifier: dict,
                    delta_field: str,
                    delta_value):
        """
        May raise AttributeError\n
        model.objects.get(**identifier).delta_field += delta_value (or create)
        if delta_field == 0: delete
        if delta_field < 0: raise
        """
        try:
            model_instance = model.objects.get(**identifier)
            new_delta_field_value = \
                getattr(model_instance, delta_field) + delta_value

            if new_delta_field_value < 0:
                raise NonPositiveCountException

            setattr(
                model_instance,
                delta_field,
                new_delta_field_value
            )

            if new_delta_field_value > 0:
                model_instance.save(update_fields=(delta_field,))

            elif new_delta_field_value == 0:
                model_instance.delete()

        except model.DoesNotExist:
            if delta_value > 0:
                model.objects.create(
                    **identifier, **{delta_field: delta_value}
                )
            else:
                raise NonPositiveCountException
