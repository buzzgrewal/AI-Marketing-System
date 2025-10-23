import re
from typing import Dict, Any, Optional
from datetime import datetime


class TemplateRenderService:
    """Service for rendering email templates with variable substitution"""

    @staticmethod
    def render_template(
        content: str,
        variables: Dict[str, Any],
        default_value: str = ""
    ) -> str:
        """
        Render a template by replacing variables with actual values.
        
        Supported formats:
        - {{variable_name}} - Simple variable
        - {{variable_name|default:"Default Value"}} - Variable with default
        - {{first_name|capitalize}} - Variable with filter
        
        Args:
            content: Template content with variables
            variables: Dictionary of variable values
            default_value: Default value for missing variables
            
        Returns:
            Rendered content with variables replaced
        """
        
        def replace_variable(match):
            """Replace a single variable match"""
            full_match = match.group(1)
            parts = full_match.split('|')
            var_name = parts[0].strip()
            
            # Get the variable value
            value = variables.get(var_name, default_value)
            
            # Apply filters if present
            if len(parts) > 1:
                for filter_part in parts[1:]:
                    filter_part = filter_part.strip()
                    
                    # Handle default filter
                    if filter_part.startswith('default:'):
                        default = filter_part.split(':', 1)[1].strip('"\'')
                        if not value:
                            value = default
                    
                    # Handle capitalize filter
                    elif filter_part == 'capitalize':
                        value = str(value).capitalize() if value else ''
                    
                    # Handle upper filter
                    elif filter_part == 'upper':
                        value = str(value).upper() if value else ''
                    
                    # Handle lower filter
                    elif filter_part == 'lower':
                        value = str(value).lower() if value else ''
                    
                    # Handle title filter
                    elif filter_part == 'title':
                        value = str(value).title() if value else ''
            
            return str(value) if value is not None else default_value
        
        # Replace all {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        rendered = re.sub(pattern, replace_variable, content)
        
        return rendered

    @staticmethod
    def extract_variables(content: str) -> list:
        """
        Extract all variable names from template content.
        
        Args:
            content: Template content
            
        Returns:
            List of variable names found in the template
        """
        pattern = r'\{\{([^}|]+)'
        matches = re.findall(pattern, content)
        variables = [match.strip() for match in matches]
        return list(set(variables))  # Remove duplicates

    @staticmethod
    def get_default_variables() -> Dict[str, str]:
        """
        Get default variables available for all templates.
        
        Returns:
            Dictionary of default variable names and descriptions
        """
        return {
            "first_name": "Recipient's first name",
            "last_name": "Recipient's last name",
            "email": "Recipient's email address",
            "company_name": "Company name",
            "unsubscribe_url": "Unsubscribe link",
            "current_year": "Current year",
            "current_date": "Current date",
            "sport_type": "Recipient's sport type (cycling, triathlon, running)",
            "customer_type": "Customer type (athlete, coach, team, bike_fitter)",
        }

    @staticmethod
    def prepare_variables(lead_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Prepare variables from lead data and system defaults.
        
        Args:
            lead_data: Dictionary with lead information
            
        Returns:
            Dictionary of all available variables
        """
        # Start with system defaults
        variables = {
            "company_name": "Premier Bike & Position One Sports",
            "current_year": datetime.now().year,
            "current_date": datetime.now().strftime("%B %d, %Y"),
            "unsubscribe_url": "{{unsubscribe_url}}",  # Will be replaced by email service
        }
        
        # Add lead data if provided
        if lead_data:
            variables.update({
                "first_name": lead_data.get("first_name", ""),
                "last_name": lead_data.get("last_name", ""),
                "email": lead_data.get("email", ""),
                "sport_type": lead_data.get("sport_type", ""),
                "customer_type": lead_data.get("customer_type", ""),
                "location": lead_data.get("location", ""),
            })
        
        return variables

    @staticmethod
    def validate_template(content: str) -> Dict[str, Any]:
        """
        Validate template syntax and structure.
        
        Args:
            content: Template content to validate
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Check for unclosed tags
        open_count = content.count('{{')
        close_count = content.count('}}')
        
        if open_count != close_count:
            errors.append(f"Mismatched template tags: {open_count} opening tags, {close_count} closing tags")
        
        # Extract variables
        variables = TemplateRenderService.extract_variables(content)
        default_vars = TemplateRenderService.get_default_variables()
        
        # Check for unknown variables
        for var in variables:
            if var not in default_vars:
                warnings.append(f"Unknown variable: {var}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "variables_found": variables,
            "variables_count": len(variables)
        }


# Singleton instance
template_service = TemplateRenderService()

