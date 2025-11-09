###################################################################################################
# STANDARDISED CRUD
###################################################################################################

from ..base import CRUDBase
from app import models, schemas

import warnings

warnings.filterwarnings("ignore")

rules = CRUDBase[models.Rule, schemas.RuleCreate, schemas.RuleUpdate](
    model=models.Rule, i18n_terms={"text": models.RuleText}
)
