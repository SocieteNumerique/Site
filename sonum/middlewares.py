class SearchDescriptionMiddleware:
    """Middleware to add search_description and seo_title to the context."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        context = response.context_data
        if not context:
            return response
        if context.get("scheme") and context.get("scheme").search_description:
            description = context.get("scheme").search_description
            seo_title = context.get("scheme").name
        elif context.get("news") and context.get("news").search_description:
            description = context.get("news").search_description
            seo_title = context.get("news").name
        elif context.get("page") and context.get("page").search_description:
            description = context.get("page").search_description
            # for pages, seo_title and title are already correctly taken in to account
        else:
            description = "Le Programme Société Numérique de l’Agence Nationale de la Cohésion des Territoires œuvre en faveur d’un numérique d’intérêt général en offrant à tous et toutes les clés d’appropriation du numérique."

        context["search_description"] = description
        context["seo_title"] = seo_title
        return response
