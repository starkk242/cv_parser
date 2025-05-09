# Import models to make them available from db.models
from db.models.resume import Resume, Education, Skill, Experience
from db.models.job import JobDescription, RequiredSkill, PreferredSkill, EducationRequirement, ExperienceRequirement
from db.models.matching import MatchResult