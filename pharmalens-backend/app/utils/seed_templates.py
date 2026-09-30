"""Seed the supported pharmaceutical compliance frameworks."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.template import ComplianceTemplate, TemplateSection


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeedSection:
    """Describe one normative section to insert or synchronize."""

    section_code: str
    title: str
    requirement_text: str
    mandatory: bool = True


@dataclass(frozen=True)
class SeedTemplate:
    """Describe one compliance framework to insert or synchronize."""

    name: str
    version: str
    description: str
    governing_body: str
    sections: tuple[SeedSection, ...]


SEED_TEMPLATES: tuple[SeedTemplate, ...] = (
    SeedTemplate(
        name="FDA 21 CFR Part 211",
        version="Current",
        description=(
            "Current good manufacturing practice requirements for finished "
            "pharmaceuticals."
        ),
        governing_body="FDA",
        sections=(
            SeedSection(
                section_code="211.22",
                title="Quality control unit",
                requirement_text=(
                    "Establish an independent quality control unit with "
                    "responsibility and authority to approve or reject "
                    "components, drug product containers, closures, in-process "
                    "materials, packaging, labeling, and finished drug products; "
                    "review production records; and approve or reject procedures "
                    "and specifications."
                ),
            ),
            SeedSection(
                section_code="211.67",
                title="Equipment cleaning and maintenance",
                requirement_text=(
                    "Equipment and utensils must be cleaned, maintained, and "
                    "sanitized at appropriate intervals to prevent contamination "
                    "or malfunction, using written procedures and records."
                ),
            ),
            SeedSection(
                section_code="211.100",
                title="Written procedures; deviations",
                requirement_text=(
                    "Written procedures for production and process control must "
                    "be drafted, reviewed, approved, followed, and documented; "
                    "deviations must be recorded and justified."
                ),
            ),
            SeedSection(
                section_code="211.113",
                title="Control of microbiological contamination",
                requirement_text=(
                    "Written procedures must be established and followed to "
                    "prevent objectionable microorganisms in non-sterile products "
                    "and microbiological contamination in products required to "
                    "be sterile."
                ),
            ),
            SeedSection(
                section_code="211.160",
                title="General laboratory requirements",
                requirement_text=(
                    "Laboratory controls, including sampling and testing "
                    "procedures, must be scientifically sound and documented; "
                    "specifications and test methods require approval by the "
                    "quality control unit."
                ),
            ),
            SeedSection(
                section_code="211.192",
                title="Production record review",
                requirement_text=(
                    "All drug product production and control records, including "
                    "packaging and labeling records, must be reviewed and "
                    "approved by the quality control unit before release; "
                    "unexplained discrepancies or failures must be thoroughly "
                    "investigated."
                ),
            ),
        ),
    ),
    SeedTemplate(
        name="EU GMP Annex 1",
        version="2022",
        description="Manufacture of sterile medicinal products.",
        governing_body="EMA",
        sections=(
            SeedSection(
                section_code="4",
                title="Premises and cleanroom classification",
                requirement_text=(
                    "Premises for sterile manufacture must be designed and "
                    "qualified to minimize contamination risks, with cleanrooms "
                    "classified and monitored against defined environmental "
                    "requirements."
                ),
            ),
            SeedSection(
                section_code="5",
                title="Equipment and sterilization",
                requirement_text=(
                    "Equipment design, qualification, maintenance, cleaning, "
                    "and sterilization must support contamination control and "
                    "aseptic processing, with sterilization processes validated "
                    "for their intended use."
                ),
            ),
            SeedSection(
                section_code="9",
                title="Environmental and process monitoring",
                requirement_text=(
                    "An environmental and process monitoring program must be "
                    "based on the contamination control strategy and include "
                    "defined alert and action limits, trend evaluation, and "
                    "investigation of adverse results."
                ),
            ),
        ),
    ),
    SeedTemplate(
        name="ICH Q10",
        version="2008",
        description="Pharmaceutical quality system guidance.",
        governing_body="ICH",
        sections=(
            SeedSection(
                section_code="2",
                title="Management responsibility",
                requirement_text=(
                    "Senior management should provide leadership, resources, "
                    "defined responsibilities, effective communication, and "
                    "periodic management review for the pharmaceutical quality "
                    "system."
                ),
            ),
            SeedSection(
                section_code="3",
                title="Continual improvement of process performance",
                requirement_text=(
                    "Process and product performance should be monitored and "
                    "evaluated through knowledge management, corrective and "
                    "preventive action, change management, and management review "
                    "to drive continual improvement."
                ),
            ),
        ),
    ),
)


async def seed_templates() -> None:
    """Insert or synchronize all supported regulatory templates and sections."""
    created_templates = 0
    created_sections = 0
    updated_sections = 0

    async with AsyncSessionLocal() as session:
        async with session.begin():
            for template_spec in SEED_TEMPLATES:
                template_result = await session.execute(
                    select(ComplianceTemplate).where(
                        ComplianceTemplate.name == template_spec.name,
                        ComplianceTemplate.version == template_spec.version,
                    )
                )
                template = template_result.scalar_one_or_none()

                if template is None:
                    template = ComplianceTemplate(
                        name=template_spec.name,
                        version=template_spec.version,
                        description=template_spec.description,
                        governing_body=template_spec.governing_body,
                    )
                    session.add(template)
                    await session.flush()
                    created_templates += 1
                else:
                    template.description = template_spec.description
                    template.governing_body = template_spec.governing_body

                section_result = await session.execute(
                    select(TemplateSection).where(
                        TemplateSection.template_id == template.id
                    )
                )
                existing_sections = {
                    section.section_code: section
                    for section in section_result.scalars().all()
                }

                for order_index, section_spec in enumerate(template_spec.sections):
                    section = existing_sections.get(section_spec.section_code)
                    if section is None:
                        session.add(
                            TemplateSection(
                                template_id=template.id,
                                section_code=section_spec.section_code,
                                title=section_spec.title,
                                requirement_text=section_spec.requirement_text,
                                mandatory=section_spec.mandatory,
                                order_index=order_index,
                            )
                        )
                        created_sections += 1
                        continue

                    section.title = section_spec.title
                    section.requirement_text = section_spec.requirement_text
                    section.mandatory = section_spec.mandatory
                    section.order_index = order_index
                    updated_sections += 1

    logger.info(
        "Regulatory templates synchronized: templates_created=%d "
        "sections_created=%d sections_updated=%d templates_total=%d "
        "sections_total=%d",
        created_templates,
        created_sections,
        updated_sections,
        len(SEED_TEMPLATES),
        sum(len(template.sections) for template in SEED_TEMPLATES),
    )


def main() -> None:
    """Run the asynchronous regulatory-template seed operation."""
    asyncio.run(seed_templates())


if __name__ == "__main__":
    main()
