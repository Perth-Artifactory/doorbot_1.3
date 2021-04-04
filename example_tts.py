# https://www.openhab.org/addons/voice/picotts/
# https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)

# https://cstan.io/?p=11840&lang=en
# (libttspico-utils: binaries not available for rpi so must compile)
# Managed to compile it 
# Using compiled and installed package --
# Create with: pico2wave -w out.wav "test 123"
# Can "aplay out.wave"

# https://pypi.org/project/ttspico/
# After compile/install above can invoke python bindings.
# However python bindings just dump the binary audio, not sure how to play