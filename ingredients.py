import wynn
import common
import sys
from river_mwclient.gamepedia_client import GamepediaClient
from river_mwclient.auth_credentials import AuthCredentials
from river_mwclient.template_modifier import TemplateModifierBase

class IngredientInfoboxModifier(TemplateModifierBase):
    def update_template(self, template):
        if ":" in self.current_page.name:
            # Ignore if page is not in the default namespace
            return

        # The name to use for API-requests priorities: api-name (template param) > name (template param) > page name
        api_name = template.get('api_name').value.strip() if template.has('api_name') else template.get('name').value.strip() if template.has('name') else self.current_page.name.strip()
        if api_name == "{{PAGENAME}}":
            api_name = self.current_page.name.strip()

        ingredient_data = wynn.ingredient.get_ingredient(api_name)
        if ingredient_data == None:
            print("No API data was found for the ingredient with the API name '{}' on the page '{}'".format(api_name, self.current_page.name))
            return

        # Construction of new template data
        skills = ""
        for skill in ingredient_data['skills']:
            skills += str.lower(skill) + ","
        skills = skills[0:-1] # Remove final comma from string
        new_infobox_data = {
            'tier': ingredient_data['tier'],
            'level': ingredient_data['level'],
            'professions': skills
            }
        new_infobox_data['name'] = ingredient_data['displayName'].replace("֎", "") if 'displayName' in ingredient_data else ingredient_data['name'].replace("֎", "")

        # Sprite retrival
        last = template.get('image').value.strip() if template.has('image') else ""
        sprite_name = common.convert_sprite(api_name, last, ingredient_data['sprite']['id'], ingredient_data['sprite']['damage'] ) 
        if sprite_name != None:
            new_infobox_data['image'] = sprite_name

        # Apply new template data
        for data in new_infobox_data:
            template.add(data, new_infobox_data[data])

class IngredientCraftingModifier(TemplateModifierBase):
    def update_template(self, template):
        if ":" in self.current_page.name:
            # Ignore if page is not in the default namespace
            return

        # The name to use for API-requests priorities: api-name (template param) > name (template param) > page name
        api_name = template.get('api_name').value.strip() if template.has('api_name') else template.get('name').value.strip() if template.has('name') else self.current_page.name.strip()
        if api_name == "{{PAGENAME}}":
            api_name = self.current_page.name.strip()

        ingredient_data = wynn.ingredient.get_ingredient(api_name)
        if ingredient_data == None:
            print("No API data was found for the ingredient with the API name '{}' on the page '{}'".format(api_name, self.current_page.name))
            return

        # Construction of new template data
        new_crafting_data = {
            **common.convert_range_identifications(ingredient_data['identifications']),
            **common.convert_position_modifiers(ingredient_data['ingredientPositionModifiers'])
            }
        if 'consumableOnlyIDs' in ingredient_data:
            new_crafting_data = {**new_crafting_data, **common.convert_single_identifications(ingredient_data['consumableOnlyIDs'])}
        if 'itemOnlyIDs' in ingredient_data:
            new_crafting_data = {**new_crafting_data, **common.convert_single_identifications(ingredient_data['itemOnlyIDs'])}
        new_crafting_data['name'] = ingredient_data['displayName'] if 'displayName' in ingredient_data else ingredient_data['name']

        # Sprite retrival
        last = template.get('icon').value.strip() if template.has('icon') else ""
        sprite_name = common.convert_sprite(api_name, last, ingredient_data['sprite']['id'], ingredient_data['sprite']['damage'] ) 
        if sprite_name != None:
            new_crafting_data['icon'] = sprite_name

        # Apply new template data
        for data in new_crafting_data:
            template.add(data, new_crafting_data[data])

print("Connecting to Wynncraft Wiki...")
credentials = AuthCredentials(user_file="me")
wiki = GamepediaClient('wynncraft', credentials=credentials)
print("Connected!")

if len(sys.argv[1:]) > 0:
    IngredientInfoboxModifier(wiki, 'Infobox/Ingredient', summary='Bot edit, update ingredient infobox template', title_list=sys.argv[1:]).run()
    IngredientCraftingModifier(wiki, 'Crafting', summary='Bot edit, update ingredient crafting template', title_list=sys.argv[1:]).run()
else:
    IngredientInfoboxModifier(wiki, 'Infobox/Ingredient', summary='Bot edit, update ingredient infobox template').run()
    IngredientCraftingModifier(wiki, 'Crafting', summary='Bot edit, update ingredient crafting template').run()
