//! Temporary local validation for the `wisp-cangjie` skill package
//! (adapted from a third-party skill). Validates with the real parser and
//! store package inspection; may be removed after use.
//!
//! Re-run: copy this file into `wisp-science/crates/wisp-skills/tests/`,
//! run `cargo test -p wisp-skills`, then delete it.

use wisp_skills::distribution::inspect_repository;
use wisp_dto::SkillInstallSource;

#[test]
fn wisp_cangjie_passes_store_inspection() {
    let name = "wisp-cangjie";
    let package_path = format!("skills/{name}");
    let repo_root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../");
    let package = repo_root.join(&package_path);
    let source = SkillInstallSource {
        repository: "xuzhougeng/wisp-science".into(),
        source_url: "https://github.com/xuzhougeng/wisp-science".into(),
        git_ref: "main".into(),
        commit: "a".repeat(40),
        package_path: package_path.clone(),
    };
    let candidates =
        inspect_repository(&repo_root, &source).expect("inspect_repository failed");
    assert_eq!(candidates.len(), 1, "expected exactly one candidate");
    let candidate = &candidates[0];
    assert!(
        candidate.format_errors.is_empty(),
        "format_errors: {:?}",
        candidate.format_errors
    );
    assert!(
        candidate.resource_errors.is_empty(),
        "resource_errors: {:?}",
        candidate.resource_errors
    );
    assert_eq!(candidate.name, name);
    assert!(!candidate.description.is_empty());

    let markdown = std::fs::read_to_string(package.join("SKILL.md")).unwrap();
    for residue in ["cangjie-skill", "kangarooking", "nuwa", "darwin", "methodology-distiller"] {
        assert!(
            !markdown.to_lowercase().contains(residue),
            "source-project residue: {residue}"
        );
    }

    // Every package resource that SKILL.md references must exist.
    let referenced = [
        "references/methodology/00-overview.md",
        "references/methodology/01-stage0-adler.md",
        "references/methodology/02-stage1-parallel-extract.md",
        "references/methodology/03-stage1.5-triple-verify.md",
        "references/methodology/03b-stage1.6-promotion-gate.md",
        "references/methodology/04-stage2-ria-plus.md",
        "references/methodology/05-stage3-zettelkasten.md",
        "references/methodology/06-stage4-pressure-test.md",
        "references/methodology/07-stage5-deliver.md",
        "references/extractors/framework-extractor.md",
        "references/extractors/principle-extractor.md",
        "references/extractors/case-extractor.md",
        "references/extractors/counter-example-extractor.md",
        "references/extractors/glossary-extractor.md",
        "references/templates/BOOK_OVERVIEW.md.template",
        "references/templates/DIGEST.md.template",
        "scripts/distill.py",
        "scripts/validate_skill_pack.py",
        "scripts/build_chunks.py",
        "scripts/build_index.py",
        "scripts/run_trigger_evals.py",
        "scripts/run_output_evals.py",
        "assets/schemas/capability-bundle.schema.json",
        "assets/schemas/source-document.schema.json",
    ];
    for rel in referenced {
        assert!(package.join(rel).exists(), "missing resource: {rel}");
    }
}
