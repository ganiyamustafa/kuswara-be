from module.game.schemas import GameRoomSchemas
import character.chr_0001.constants as constants

# steal skill
def steal(game_room: GameRoomSchemas, calculation_point_data: dict, updated_data: dict) -> dict:
  participants = game_room.participants
  all_point = sum(calculation_point_data.values())
  tmp_updated_data = updated_data.copy()
  is_use_skill = False

  # loop participant
  for participant in participants:
    # reset all updated point
    tmp_updated_data[f'participants.${participant.id}.point'] -= calculation_point_data[participant.id]
    if participant.user_character and constants.code == participant.user_character.code and participant.user_character.skills and participant.user_character.skills[0].is_active:
      # add all updated point to user who use skill
      tmp_updated_data[f'participants.${participant.id}.point'] += all_point

      # set is use skill to true
      is_use_skill = True

  # return data
  return tmp_updated_data if is_use_skill else updated_data