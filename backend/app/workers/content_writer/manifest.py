from app.core.workforce import WorkerManifest


CONTENT_WRITER = WorkerManifest(
    worker_id="content_writer",
    name="Content Writer",
    description="Creates marketing content.",
    version="1.0.0",
    capabilities=(
        "copywriting",
        "blog_writing",
        "email_marketing",
        "facebook_posts",
        "linkedin_posts",
        "marketing_content",
    ),
    supported_executives=(
        "marketing",
    ),
)