
##################################################################################################################################################################
###############    EXPERIMENT INITIALIZE     #####################################################################################################################
##################################################################################################################################################################

### Alpha Spatial Cue with edits to reflect Foster et al 2020 (DOI: https://doi.org/10.1523/JNEUROSCI.2962-19.2020)
###
### Each run of script runs one block of experiment
### Target and Distractor trials are blocked
### Two visits per subject
### No enforced response time, but trials will move on after a few seconds
### Target stim and neutral colors remain the same trial-by-trial, distractor color changes
###
### 06/27/2021: Debugging the spatial cue version to make sure it runs smoothly in EEG, and adjusted to match Foster et al 2020

from __future__ import absolute_import, division
from psychopy import locale_setup, sound, gui, visual, core, data, event, logging, clock
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, normal, shuffle,uniform,permutation
import os  # handy system and path functions
import sys  # to get file system encoding
import serial #for sending triggers from this computer to biosemi computer
import csv
import copy
from psychopy import visual, core

expInfo = {'subject': '', 'session [t or d]':'d','run':'','visit':'1','refresh':60,'colorCode [1-5]':'2'}
expName='alpha_singleton_ColorConstant_Sledgehammer_Foster'
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
win = visual.Window([1280,720],units='deg',fullscr=True,monitor='testMonitor',checkTiming=True,colorSpace='rgb255',color=[0,0,0]) #[1680,1050] #[1280,720]

# the vis_deg_cue and the multiplier should multiply to equal changing to match foster @ 4 degrees # 4.66
vis_deg_multiplier=3.33333#3.883333#5.17777778
vis_deg_cue=1.2#0.9
no_stim=8 #6

cue_time=0.1
delay_one=0.9
probe_time=0.6
#response_time=3 # no max response time, but will move on after 5 seconds without input

num_blocks=1 # blocks per run of the script
blocks={}

# Activate the EEG triggers, set EEGflag to zero for debugging 
EEGflag=1

for key in ['escape']:
    event.globalKeys.add(key, func=core.quit)
    

##################################################################################################################################################################
###############    DEFINE FUNCTIONS     ##########################################################################################################################
##################################################################################################################################################################

def checkExpInfo(expInfo):
    ## t= target, d= distractor, this is the shape that the spatial cue is pointing to for this whole run! 
    if expInfo['session [t or d]']=='t':
        cue_type='tar'
    elif expInfo['session [t or d]']=='d':
        cue_type='dis'
    else:
        print('Please enter a valid response to the SESSION box')
        core.quit()
    ## color code
    if expInfo['colorCode [1-5]'] not in ['1','2','3','4','5']:
        print("Please enter a valid response to the ColorCode box")
        core.quit()
    else:
        color_code=expInfo['colorCode [1-5]']
    ## two sessions per subject
    if expInfo['visit'] not in ['1','2']:
        print("Please enter a valid response to the Run box")
        core.quit()
    else:
        visit_num=expInfo['visit']
    ## which blocks this is 
    if expInfo['run'] not in ['1','2','3','4','5','6','7','8','9','10']:
        print("Please enter a valid response to the Run box")
        core.quit()
    else:
        thisRunNum=expInfo['run']
    refresh_rate=expInfo['refresh']

    return cue_type, thisRunNum, refresh_rate,color_code,visit_num
# return cue_type, thisRunNum, refresh_rate,color_code,visit_num

def pracCond(n_practrials=8,demo=False):
    # the practice is set up to run distractor cue trials, but as of right now not target cues
    pracDataList=[]
    pracBlock=[]
    for r in range(int(n_practrials)):
        pracBlock.append('dis')
        pracBlock.append('neut')
    for trial in range(n_practrials):
        ITI=2.0
        distractor_stim,target_stim,other_stim,other_name=generate_target(dist_color,neut_color,target_color,stimuli,cue_type)
        if trial==0:
            if demo:
                prac_msg=visual.TextStim(win, pos=[0,.5], units='norm',text='Press any key to begin a demo!')
                prac_msg.draw()
                win.flip()
                event.waitKeys()
            elif not demo:
                prac_msg=visual.TextStim(win, pos=[0,.5], units='norm',text='Press any key to begin the practice')
                prac_msg.draw()
                win.flip()
                event.waitKeys()
        for circs in  stimuli:
            print(circs.size)
            circs.autoDraw=False
        
        if pracBlock[trial]=='neut':
            cue_circ=list(np.random.choice(stimuli,no_stim,replace=False))
            for c in cue_circ:
                #c.setLineColor([255,255,255])
                c.autoDraw=True
        elif pracBlock[trial]==cue_type:
            cue_circ=np.random.choice(stimuli,1)
            cue_circ[0].autoDraw=True
            #cue_circ[0].setLineColor([255,255,255])
        
        fixation.autoDraw=True
        
        if not demo:
            prac_cue_time=cue_time
        else:
            prac_cue_time=1
        
        wait_here(prac_cue_time) # ############################## Cue presentation ###################
        
        ## stage fixation
        fixation.autoDraw=True
        for circs in stimuli:
            circs.autoDraw=False
        for placeholder in placeholdersDia:
            placeholder.autoDraw=True
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=True
        
        #if EEGflag:
        #    # port.flush()
        #    win.callOnFlip(port.write,bytes([delay_one_trig]))
        
        if not demo:
            prac_delay_time=delay_one
        else:
            prac_delay_time=1
        
        wait_here(prac_delay_time) # ############################### delay one/SOA period ###############
        
        for placeholder in placeholdersDia:
            placeholder.autoDraw=False
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=False
        
        if pracBlock[trial]=='dis':
            cue_loc=list(stimuli).index(cue_circ[0]) #index of the distractor cue circle
            stim_minus_cue=np.delete(stimuli, cue_loc) #get a list of circles that don't include the distractor cue circ
            which_circle=np.random.choice(stim_minus_cue,1)[0] # choose the target loc
            distractor_stim_clock=(cue_circ[0].pos[0]*vis_deg_multiplier,cue_circ[0].pos[1]*vis_deg_multiplier)
            distractor_stim.pos=(distractor_stim_clock[0],distractor_stim_clock[1])#(distractor_stim_clock[0]/6,distractor_stim_clock[1]/6)
            distractor_stim.autoDraw=True
            disAorP='P'
            target_stim.pos=(which_circle.pos[0]*vis_deg_multiplier,which_circle.pos[1]*vis_deg_multiplier)#(which_circle.pos[0]/6,which_circle.pos[1]/6)
            target_stim.autoDraw=True
        elif pracBlock[trial]=='neut': 
            which_circle=np.random.choice(stimuli,1)[0]
            disAorP='A'
            if disAorP=='P':
                tar_loc=list(stimuli).index(which_circle)
                stim_minus_tar=np.delete(stimuli,tar_loc)
                distractor_stim_clock=np.random.choice(stim_minus_tar,1)[0].pos
                distractor_stim_clock=(distractor_stim_clock[0]*vis_deg_multiplier,distractor_stim_clock[1]*vis_deg_multiplier)
                distractor_stim.pos=(distractor_stim_clock[0],distractor_stim_clock[1])#(distractor_stim_clock[0]/6,distractor_stim_clock[1]/6)
                distractor_stim.autoDraw=True
            target_stim.pos=(which_circle.pos[0]*vis_deg_multiplier,which_circle.pos[1]*vis_deg_multiplier)#(which_circle.pos[0]/6,which_circle.pos[1]/6)
            target_stim.autoDraw=True
        elif thisBlock[trial]=='tar':
            stim_minus_cue=np.delete(stimuli, cue_loc) #get a list of circles that don't include the target cue circ
            which_circle=cue_circ # which_circle is always assigned as the target, since this is target cue condition we already know where which_circle is located
            target_stim_clock=(which_circle.pos[0]*vis_deg_multiplier,which_circle.pos[1]*vis_deg_multiplier)
            target_stim.pos=(target_stim_clock[0],target_stim_clock[1])
            target_stim.autoDraw=True
            distractor_stim_clock=np.random.choice(stim_minus_cue,1)[0].pos
            distractor_stim_clock=(distractor_stim_clock[0]*vis_deg_multiplier,distractor_stim_clock[1]*vis_deg_multiplier)
            distractor_stim.pos=(distractor_stim_clock[0],distractor_stim_clock[1])#(distractor_stim_clock[0]/6,distractor_stim_clock[1]/6)
            distractor_stim.autoDraw=True
            disAorP='P'
        
        
        #distractor_stim.ori= (np.random.choice([0,90,180,270],1))[0] #choose the orientation of the distractor
        for s in range(len(stimuli)):
            circs=stimuli[s]
            bars[s].pos=other_stim[s].pos #except target and distractor
            bars[s].ori=(np.random.choice([0,90],1))[0]
            bars[s].autoDraw=True
            if not ((circs.pos[0]==which_circle.pos[0]) and (circs.pos[1]==which_circle.pos[1])):  # if this position isn't the target
                if ((pracBlock[trial]=='neut' and disAorP=='P') or pracBlock[trial]=='dis'): #if this trial has a distractor 
                    if not ((circs.pos[0]==(distractor_stim_clock[0]/vis_deg_multiplier)) and (circs.pos[1]==(distractor_stim_clock[1]/vis_deg_multiplier))): # and if this position is also not the distractor
                        #if the circle is not a target or distractor then put other_stim in it
                        other_stim[s].autoDraw=True
                else:
                    other_stim[s].autoDraw=True
            elif ((circs.pos[0]==which_circle.pos[0]) and (circs.pos[1]==which_circle.pos[1])): # if it is the target position
                target_ori=bars[s].ori #then document the orientation of the bar at this loc
                print(target_ori)
        
        if target_ori==0:
            corrKey='q'#'up'
        elif target_ori==90:
            corrKey='p'#'left'
        
        if not demo:
            prac_probe_time=delay_one
        else:
            prac_probe_time=3
        wait_here(prac_probe_time) # ############### probe presentation ####################
        
        ## stage fixation
        fixation.autoDraw=True
        for circs in stimuli:
            circs.autoDraw=False
        target_stim.autoDraw=False
        distractor_stim.autoDraw=False
        for s in other_stim:
            s.autoDraw=False
        for placeholder in placeholdersDia:
            placeholder.autoDraw=True
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=True
            
        #wait_here(2) # ############### response ####################
        
        event.clearEvents()
        if not demo:
            prac_resp_time=30
        else:
            prac_resp_time=2
            
        max_win_count=int(prac_resp_time/(1/refresh_rate))
        win_count=0
        subResp=None
        clock=core.Clock()
        while not subResp:
            win.flip()
            subResp=event.getKeys(keyList=['q','p'], timeStamped=clock)#['up','left']
            win_count=win_count+1
            if win_count==max_win_count:
                break
        
        if not subResp:

            trial_corr=0

        else:

            if subResp[0][0]==corrKey:
                trial_corr=1
            else:
                trial_corr=0
        pracDataList.append(trial_corr)
        fixation.draw()
        for circs in stimuli:
            circs.autoDraw=False
        for shape in other_stim:
            shape.autoDraw=False
        for bar in bars:
            bar.autoDraw=False
        target_stim.autoDraw=False
        distractor_stim.autoDraw=False
        for placeholder in placeholdersDia:
            placeholder.autoDraw=False
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=False
        
        win.flip()
        core.wait(ITI)
        
    if not demo:
        #fixation.color=([0,0,0])
        acc_feedback=visual.TextStim(win, pos=[0,.5],units='norm',text='Your accuracy for the practice round was %i percent. Practice again? (y/n)' %(100*(np.sum(pracDataList)/n_practrials)))
        acc_feedback.draw()
        win.update()
        cont=event.waitKeys(keyList=['y','n'])
        if cont[0]=='y':
            display_instructions(cue_type)
            pracCond(n_practrials)
 
def wait_here(t):
    interval=1/refresh_rate
    num_frames=int(t/interval)
    for n in range(num_frames): #change back to num_frames
        fixation.draw()
        win.flip()

def make_ITI():
    if not EEGflag:
        ITI=np.random.choice([1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6],1)[0] #averages to around 2 second?
    else:
        ITI=np.random.choice([2.5,2.6,2.7,2.8,2.9,3,3.1,3.2,3.3,3.4,3.5],1)[0] # averages to around 3 seconds?
    return ITI
# return ITI

def make_csv(filename,blocks,thisRunNum,color_code,expStart=False):
    with open(filename+'.csv', mode='w') as csv_file:
        #'trialNum':(trial),'trial_type':thisBlock,'dis_type':neutCue_type,'corrResp':corrKey,'subjectResp':key,'trialCorr?':trial_corr,'RT':RT, 'stim_loc':stim_loc,'ITI':ITI,'trial_trigs':(thistrialFlag,probetrig,resp_trig)
        #fieldnames=['block','trialNum','trial_type','dis_PresentorAbsent','corrResp','subResp','trialCorr?','RT','stim_loc(T,D)','ITI','Tar,Dis,Other','trial_trigs','triggers']
        
        FirstBlock=blocks['0'] #blocks is a dictionary of the block data, ie { 0 : [{trial:1,RT:1,etc },{trial:2,RT:2,etc},... ] }
        FirstTrial=FirstBlock[0]
        fieldnames=list(FirstTrial.keys()) + ['block','triggers','run','colorCode']
        #fieldnames is simply asserting the categories at the top of the CSV
        writer=csv.DictWriter(csv_file,fieldnames=fieldnames)
        writer.writeheader()
        print('\n\n\n')
        for n in range(len(blocks.keys())): # loop through each block
            ThisTrialList=blocks[str(n)] #grabbing the block info for this block
            #print(ThisBlock)
            #print('\n')
            for k in range(len(ThisTrialList)): #this should be the # of trials
                ThisTrial=ThisTrialList[k] #grabbing the trial info out of data for this trial
                #print(ThisTrial)
                
                #combining all the dictionaries into one to write to row
                dataDict= ThisTrial.copy()
                dataDict.update({'block':str(n)})
                dataDict.update({'run':thisRunNum,'colorCode':color_code})
                if EEGflag and expStart==True and k==0:
                     dataDict.update({'triggers':(cue_trigDict,probe_trigDict,other_trigDict)})
                else:
                    dataDict.update({'triggers':''})
                
                writer.writerow(dataDict)

def generate_target(dist_color,neut_color,target_color,stimuli,cue_type):
    ## generate_target() gives the shapes that will become the target, distractor, and neutral shapes. can be called once per block or per trial, depending on how often you want colors to be changed out
    potential_dis_shapes=[shape for shape in images_names if dist_color in shape]
    distractor_name=np.random.choice(potential_dis_shapes,1)[0]
    
    colors_list=['red','blue','pink','yellow','orange']
    
    if 'circle' in distractor_name:
        target_shape='diamond'
        other_shape='circle'
    elif 'diamond' in distractor_name:
        target_shape='circle'
        other_shape='diamond'
    
    distractor_stim=images[distractor_name]
    target_stim=images[neut_color+'_'+target_shape]
    #if cue_type =='dis':
    #    target_stim=images[neut_color+'_'+target_shape]
    #elif cue_type=='tar':
    #    target_stim=images[target_color+'_'+target_shape] # we don't want the target to be  a color singleton right now, but might want that to be true some other version
    
    other_name=neut_color+'_'+other_shape
    other_stim=[visual.ImageStim(win=win,image=images[other_name].image, units='deg',ori=0,size=images[other_name].size,name=other_name) for i in range(no_stim)] # making 4 copies of Other_shape 
    for g in range(no_stim):
        #other_stim[g].autoDraw=True
        other_stim[g].pos=(stimuli[g].pos[0]*vis_deg_multiplier,stimuli[g].pos[1]*vis_deg_multiplier)#(stimuli[g].pos[0]/6,stimuli[g].pos[1]/6)#
        #print(stimuli[g].pos)
    
    print(target_stim.name)
    print(distractor_stim.name)
    print(other_stim[0].name)
    
    for stim in stimuli:
        stim.size=(2.0,2)#(0.47,1.17)
        #stim.lineWidth=0.80#0.47
        #stim.pos=(stim.pos[0],stim.pos[1])
    
    distractor_stim.opacity=1
    target_stim.opacity=1
    
    return distractor_stim,target_stim,other_stim,other_name
# return distractor_stim,target_stim,other_stim,other_name

def display_instructions(cue_type):
    ## Display task instruction screens
    intro_msg= visual.TextStim(win, pos=[0, .5],units='norm', text='Welcome to the experiment!')
    intro_msg2= visual.TextStim(win, pos=[0, 0], units='norm',text='You will see a series circles, then a series of shapes. You must find the shape that is unique. This is the target shape.')#You must find the target shape. The target shape is the %s' % (target_stim.name.split('_')[0])+' '+(target_stim.name.split('_')[1]))
    intro_msg3=visual.TextStim(win, pos=[0,-0.5],units='norm',text='Press any key to continue')
    intro_msg.draw()
    intro_msg2.draw() 
    intro_msg3.draw()
    win.flip()
    event.waitKeys()
    intro_mesg4= visual.TextStim(win,pos=[0,.6],units='norm',text='Please remain focused on the cross in the middle of the screen whenever there are NOT circles on the screen.')
    intro_mesg5=visual.TextStim(win,pos=[0,0], units='norm',text='Respond to the orientation of the line in the target shape using the Q and P keys on the keyboard')
    intro_mesg6=visual.TextStim(win,pos=[0,-0.6],units='norm',text='You will also sometimes see a pop-out color. The cue lines help you find the unique shape, while ignoring the pop-out color. Press any key to continue.')
    intro_mesg4.draw()
    intro_mesg5.draw()
    intro_mesg6.draw()
    win.flip()
    event.waitKeys()
    instruction_slide1=visual.ImageStim(win=win,image=os.getcwd()+'/instruction_slides/Slide1.JPG')
    instruction_slide1.draw()
    win.flip()
    event.waitKeys()
    if cue_type =='dis':
        instruction_slide2=visual.ImageStim(win=win,image=os.getcwd()+'/instruction_slides/distractorCueInst.JPG')
        instruction_slide2.draw()
    elif cue_type =='tar':
        instruction_slide2=visual.ImageStim(win=win,image=os.getcwd()+'/instruction_slides/targetCueInst.png')
        instruction_slide2.draw()
    win.flip()
    event.waitKeys()

def set_stimuli_params(win, color_code,no_stim,vis_deg_cue):
    
    diamond_size=(4.66,3.6)
    circ_size=(4.66,3.6)
    fixation_size=0.6
    disc_bar_size=(1.4,1.63)
    
    ## Import images
    images={'blue_diamond':visual.ImageStim(win=win,name='blue_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/blue_diamond_eq.png'),
        'orange_diamond':visual.ImageStim(win=win,name='orange_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/orange_diamond.png'),
        'green_diamond':visual.ImageStim(win=win,name='green_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/green_diamond.png'),
        'pink_diamond':visual.ImageStim(win=win,name='pink_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/pink_diamond.png'),
        'red_diamond':visual.ImageStim(win=win,name='red_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/red_diamond_eq.png'),
        'yellow_diamond':visual.ImageStim(win=win,name='yellow_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/yellow_diamond_eq.png'),
        'blue_circle':visual.ImageStim(win=win,name='blue_circle', units='deg', 
        ori=0, size=circ_size,image=os.getcwd()+'/stimuli/blue_circle_eq.png'),
        'red_circle':visual.ImageStim(win=win,name='red_circle', units='deg', 
        ori=0, size=circ_size,image=os.getcwd()+'/stimuli/red_circle_eq.png'),
        'yellow_circle':visual.ImageStim(win=win,name='yellow_circle', units='deg', 
        ori=0, size=circ_size,image=os.getcwd()+'/stimuli/yellow_circle_eq.png'),
        'orange_circle':visual.ImageStim(win=win,name='orange_circle', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/orange_circle.png'),
        'pink_circle':visual.ImageStim(win=win,name='pink_circle', units='deg', 
        ori=0, size=circ_size,image=os.getcwd()+'/stimuli/pink_circle.png'),
        'green_circle':visual.ImageStim(win=win,name='green_circle', units='deg', 
        ori=0, size=circ_size,image=os.getcwd()+'/stimuli/green_circle.png'),
        'grey_diamond':visual.ImageStim(win=win,name='grey_diamond', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/grey_diamond.png'),
        'grey_circle':visual.ImageStim(win=win,name='grey_circle', units='deg', 
        ori=0, size=diamond_size,image=os.getcwd()+'/stimuli/grey_circle.png')}
    images_names=list(images.keys())
    
    ## Set up cue locations
    noon_oclock = visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
            win=win, name='12',
            ori=0, pos=(0, vis_deg_cue), units='deg',
            opacity=1, depth=0.0, interpolate=True)
    noon_oclock.setAutoDraw(True)
    
    one_oclock = visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
            win=win, name='1', units='deg',
            ori=45, pos=(vis_deg_cue*(sqrt(2)/2), ((sqrt(2)/2)*vis_deg_cue)),
            opacity=1, depth=-1.0, interpolate=True)
    one_oclock.setAutoDraw(True)
    
    three_oclock = visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
        win=win, name='3',
        ori=90, units='deg', 
        pos=(vis_deg_cue, 0),
        opacity=1, depth=-3.0, interpolate=True)
    three_oclock.setAutoDraw(True)
    
    five_oclock = visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
        win=win, name='5',
        ori=135, pos=(vis_deg_cue*(sqrt(2)/2), -((sqrt(2)/2)*vis_deg_cue)),
        opacity=1, depth=-5.0, interpolate=True)
    five_oclock.setAutoDraw(True)
    
    six_oclock = visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
        win=win, name= '6',  ori=0, pos=(0, -vis_deg_cue),
        opacity=1, depth=-5.0, interpolate=True)
    six_oclock.setAutoDraw(True)
    
    seven_oclock =visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
        win=win, name='7',
        ori=225, pos=(-vis_deg_cue*(sqrt(2)/2), -((sqrt(2)/2)*vis_deg_cue)),
        opacity=1, depth=-5.0, interpolate=True)
    seven_oclock.setAutoDraw(True)
    
    nine_oclock = visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
        win=win, name='9',
        ori=90, pos=(-vis_deg_cue, 0),
        opacity=1, depth=-3.0, interpolate=True)
    nine_oclock.setAutoDraw(True)
    
    eleven_oclock =visual.ImageStim(image=os.getcwd()+'/stimuli/grey_Verticle.png',
        win=win, name='11',
        ori=315, pos=(-vis_deg_cue*(sqrt(2)/2), ((sqrt(2)/2)*vis_deg_cue)),
        opacity=1, depth=-1.0, interpolate=True)
    eleven_oclock.setAutoDraw(True)
    
    stimuli=[noon_oclock, one_oclock,three_oclock,five_oclock,six_oclock, seven_oclock,nine_oclock,eleven_oclock]
    right_stim=stimuli[:4]
    left_stim=stimuli[4:]
    
    colors_list=['red','blue','pink','yellow','orange']
    neut_color='green'#two_colors[0] #neutral is always green now
    dist_color=colors_list[int(color_code)-1] #using the color code as the index
    if color_code=='6':
        target_color=colors_list[0]
    else:
        target_color=colors_list[int(color_code)]
    
    fixation = visual.TextStim(win, text='+',pos=(0,0.005),units='norm', color=(1,1,1))
    fixation.size= fixation_size
    
    bars=[visual.ImageStim(win=win,name='bar', units='deg', ori=0,size=disc_bar_size,image=os.getcwd()+'/stimuli/grey_Verticle.png')  for i in range(no_stim)]
    
    placeholdersDia=[visual.ImageStim(win=win,name=('GreyDia%i'%(i)), units='deg', 
        ori=0,size=diamond_size,image=images['grey_diamond'].image,
        pos=(stimuli[i].pos[0]*vis_deg_multiplier,stimuli[i].pos[1]*vis_deg_multiplier))
        for i in range(no_stim)]
    placeholdersCirc=[visual.ImageStim(win=win,name=('GreyCirc%i'%(i)), units='deg', 
        ori=0,size=circ_size,image=images['grey_circle'].image,
        pos=(stimuli[i].pos[0]*vis_deg_multiplier,stimuli[i].pos[1]*vis_deg_multiplier))
        for i in range(no_stim)]

    for circs in stimuli:
        circs.autoDraw=False

    return images, images_names, fixation, stimuli, left_stim, right_stim, neut_color, dist_color, bars, target_color,placeholdersDia,placeholdersCirc
# return images, images_names, fixation, stimuli, left_stim, right_stim, neut_color, dist_color, bars, target_color,placeholdersDia

def generate_trial_params(cue_type, no_stim, num_blocks, n_neut=32, n_cue=32):
    stimList=[] #list of trials
    cuePosList=[]
    neutCue=[] # of the neutral blocks, 16 are DisA and 16 are DisP
    bar_ori=[]
    
    # Sledgehammer: 
    # 64 trials in ea block 
    # 4/8 of all trials should be neutral (2/8 P, 2/8 A), 4/8 spatial cues (distractor or target)
    
    for n in range(n_neut): #hard coding the # of trials to match brad
        stimList.append('neut')
    for n in range(n_cue): 
        stimList.append(cue_type)
    
    for n in range(int(n_cue/no_stim)): #hopefully this divides evenly (it does if only 6 circles)
        for no_position in range(no_stim):
            cuePosList.append(no_position) # will append one of each circle position ea time it loops, to control for the number of times any one circle position is cued
    
    for n in range(int(no_stim/2)):
        bar_ori.append(90)
        bar_ori.append(0)
    
    stimList_blocks=[] #list of blocks, which contains a list of trials
    for n in range(num_blocks): 
        stimList_scramble=list(np.random.permutation(stimList))
        stimList_blocks.append(stimList_scramble)
    
    for r in range(16):# we assign these to each neutral trial by calling this list and popping off the P's or A's until the end of the loop
        neutCue.append('P')
    for r in range(16):
        neutCue.append('A')
    
    return stimList_blocks, cuePosList, neutCue, bar_ori
# return stimList_blocks, cuePosList, neutCue, bar_ori

def runBlock(stimList_blocks, neutCue, cuePosList, block, bar_ori):
    # ######################################### Initialize start screen
    trialDataList=[]
    fixation.color=([0,0,0])
    
    if block !=0:
        info_msg2=visual.TextStim(win, pos=[0,.5], units='norm',text='Press any key to continue to the next block')
    else:
        info_msg2=visual.TextStim(win, pos=[0,.5], units='norm',text='Press any key to begin experiment')
    info_msg2.draw()
    win.flip()
    key1=event.waitKeys()
    
    ## Display pre-block fixation
    fixation.color=([1,1,1])
    fixation.text='+'
    fixation.draw()
    win.flip() 
    core.wait(3)# pre-block pause
    thisBlock=stimList_blocks[block]
    
    print(thisBlock)
    neutCue_scramble=list(np.random.permutation(neutCue))
    cuePosList_scramble=list(np.random.permutation(cuePosList)) # this is a scrambled list of clock positions to cue to, the len of the number of cue_type trials 
    
    if EEGflag:
        port.write(startBlockflag)
         
    # ########################################### Enter trial loop
    for trial in range(len(thisBlock)):
        
        ## Randomize shapes (diamonds, circles) every trial
        distractor_stim,target_stim,other_stim,other_name=generate_target(dist_color,neut_color,target_color,stimuli,cue_type)
        ITI=make_ITI()
        
        print(thisBlock[trial])
        for circs in  stimuli:
            print(circs.size)
            circs.autoDraw=False
        for p in placeholdersDia:
            p.autoDraw=False
        for p in placeholdersCirc:
            p.autoDraw=False
        
        ## Stage cue lines and placeholder shapes
        if thisBlock[trial]=='neut': # if this is a neutral trial, then we draw all the cues and all the placeholders 
            for c in range(len(stimuli)):
                stimuli[c].autoDraw=True
                placeholdersDia[c].autoDraw=True
                placeholdersCirc[c].autoDraw=True
        elif thisBlock[trial]==cue_type: # otherwise, we pick a place to cue randomly, and we point the cue there and place a placeholder there too
            cue_loc=cuePosList_scramble.pop()
            cue_circ=stimuli[cue_loc]
            cue_circ.autoDraw=True
            #placeholdersDia[cue_loc].autoDraw=True # place placeholders in all locations even during informative cue
            #placeholdersCirc[cue_loc].autoDraw=True
            for c in range(len(stimuli)):
                placeholdersDia[c].autoDraw=True
                placeholdersCirc[c].autoDraw=True
            
        fixation.autoDraw=True
        
        ## Stage EEG trigger
        if EEGflag:
            thistrialFlag=cue_trigDict[thisBlock[trial]+'_cue_trig']
            win.callOnFlip(port.write,bytes([thistrialFlag]))
        
        wait_here(cue_time) # ############################## Cue presentation ###################
        
        ## stage fixation
        fixation.autoDraw=True
        for circs in stimuli:
            circs.autoDraw=False
        for placeholder in placeholdersDia:
            placeholder.autoDraw=True
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=True
        
        if EEGflag:
            # port.flush()
            win.callOnFlip(port.write,bytes([delay_one_trig]))
        
        wait_here(delay_one) # ############################### delay one/SOA period ###############
        
        for placeholder in placeholdersDia:
            placeholder.autoDraw=False
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=False
        
        ## stage search array
        if thisBlock[trial]=='dis':
            #cue_loc is index of the distractor cue circle
            stim_minus_cue=np.delete(stimuli, cue_loc) #get a list of circles that don't include the distractor cue circ
            which_circle=np.random.choice(stim_minus_cue,1)[0] # choose the target loc randomly, as long as it's not the distractor 
            distractor_stim_clock=(cue_circ.pos[0]*vis_deg_multiplier,cue_circ.pos[1]*vis_deg_multiplier)
            distractor_stim.pos=(distractor_stim_clock[0],distractor_stim_clock[1])#(distractor_stim_clock[0]/6,distractor_stim_clock[1]/6)
            distractor_stim.autoDraw=True
            target_stim.pos=(which_circle.pos[0]*vis_deg_multiplier,which_circle.pos[1]*vis_deg_multiplier)
            target_stim.autoDraw=True
            disAorP='P'
        elif thisBlock[trial]=='tar':
            #cue_loc=list(stimuli).index(cue_circ[0]) #index of the tar cue circle
            stim_minus_cue=np.delete(stimuli, cue_loc) #get a list of circles that don't include the target cue circ
            which_circle=cue_circ # which_circle is always assigned as the target, since this is target cue condition we already know where which_circle is located
            target_stim_clock=(which_circle.pos[0]*vis_deg_multiplier,which_circle.pos[1]*vis_deg_multiplier)
            target_stim.pos=(target_stim_clock[0],target_stim_clock[1])
            target_stim.autoDraw=True
            distractor_stim_clock=np.random.choice(stim_minus_cue,1)[0].pos
            distractor_stim_clock=(distractor_stim_clock[0]*vis_deg_multiplier,distractor_stim_clock[1]*vis_deg_multiplier)
            distractor_stim.pos=(distractor_stim_clock[0],distractor_stim_clock[1])#(distractor_stim_clock[0]/6,distractor_stim_clock[1]/6)
            distractor_stim.autoDraw=True
            disAorP='P'
        elif thisBlock[trial]=='neut': 
            which_circle=np.random.choice(stimuli,1)[0]
            disAorP=neutCue_scramble.pop()
            if disAorP=='P':
                tar_loc=list(stimuli).index(which_circle)
                stim_minus_tar=np.delete(stimuli,tar_loc)
                distractor_stim_clock=np.random.choice(stim_minus_tar,1)[0].pos
                distractor_stim_clock=(distractor_stim_clock[0]*vis_deg_multiplier,distractor_stim_clock[1]*vis_deg_multiplier)
                distractor_stim.pos=(distractor_stim_clock[0],distractor_stim_clock[1])#(distractor_stim_clock[0]/6,distractor_stim_clock[1]/6)
                distractor_stim.autoDraw=True
            target_stim.pos=(which_circle.pos[0]*vis_deg_multiplier,which_circle.pos[1]*vis_deg_multiplier)
            target_stim.autoDraw=True
        
        ## stage the response bars and the nontarget shapes
        bar_ori_scramble=list(np.random.permutation(bar_ori))
        for s in range(len(stimuli)):
            circs=stimuli[s]
            bars[s].pos=other_stim[s].pos #except target and distractor
            bars[s].ori=bar_ori_scramble[s]#(np.random.choice([0,90],1))[0]
            bars[s].autoDraw=True
            if not ((circs.pos[0]==which_circle.pos[0]) and (circs.pos[1]==which_circle.pos[1])):  # if this position isn't the target
                if ((thisBlock[trial]=='neut' and disAorP=='P') or thisBlock[trial]==cue_type): #if this trial has a distractor 
                    if not ((circs.pos[0]==(distractor_stim_clock[0]/vis_deg_multiplier)) and (circs.pos[1]==(distractor_stim_clock[1]/vis_deg_multiplier))): # and if this position is also not the distractor
                        #if the circle is not a target or distractor then put other_stim in it
                        other_stim[s].autoDraw=True
                else:
                    other_stim[s].autoDraw=True
            elif ((circs.pos[0]==which_circle.pos[0]) and (circs.pos[1]==which_circle.pos[1])): # if it is the target position
                target_ori=bars[s].ori #then document the orientation of the bar at this loc
                print(target_ori)
        
        ## response mapping
        if target_ori==0:
            corrKey='q'#'up'
        elif target_ori==90:
            corrKey='p'#'left'
        
        ## stage EEG triggers
        if EEGflag:
                # port.flush()
                probetrig=probe_trigDict[thisBlock[trial]+disAorP+'_probe_trig']
                win.callOnFlip(port.write,bytes([probetrig]))
        
        #wait_here(probe_time) # ############### probe presentation ####################
        
        #wait_here(response_time) # ############################### response ###############
        
        #if EEGflag:
        #    # port.flush()
        #    win.callOnFlip(port.write,bytes([response_period_trig]))
        
        event.clearEvents()
        max_win_count=int(5/(1/refresh_rate)) # response times out after 5 secs
        win_count_past_probe = int(probe_time/(1/refresh_rate)) #600 ms probe / (1/60) = 36ish windows
        print(win_count_past_probe)
        response_period_has_been_triggered = 0
        win_count=0
        subResp=None
        clock=core.Clock()
        while not subResp:
            win.flip() #probetrig is sent out here during first flip
            subResp=event.getKeys(keyList=['q','p'], timeStamped=clock)#['up','left']
            win_count=win_count+1
            if win_count==max_win_count:
                break
            
            if (win_count >= win_count_past_probe) and (response_period_has_been_triggered==0): # once the window flips reach probe_time, switch to the response period and wait for response
                ## nesting response period into the response while loop
                response_period_has_been_triggered=1
                
                if EEGflag:
                    port.write(bytes([response_period_trig]))
                
                fixation.autoDraw=True
                for circs in stimuli:
                    circs.autoDraw=False
                target_stim.autoDraw=False
                distractor_stim.autoDraw=False
                for s in other_stim:
                    s.autoDraw=False
                for placeholder in placeholdersDia:
                    placeholder.autoDraw=True
                for placeholder in placeholdersCirc:
                    placeholder.autoDraw=True
        
        
        
        if not subResp:
            if EEGflag:
                port.write(bytes([subNonRespTrig]))
                resp_trig=subNonRespTrig
            
            trial_corr=np.nan
            RT=np.nan
            key='None'
        else:
            if EEGflag:
                port.write(bytes([subRespTrig]))
                resp_trig=subRespTrig
            if subResp[0][0]==corrKey:
                trial_corr=1
            else:
                trial_corr=0
                
            RT=subResp[0][1]
            key=subResp[0][0]
        
        fixation.draw()
        for circs in stimuli:
            circs.autoDraw=False
            #circs.lineColorSpace='rgb255'
            #circs.setLineColor([0,0,0])
            #circs.setFillColor([0,0,0])
        for shape in other_stim:
            shape.autoDraw=False
        for bar in bars:
            bar.autoDraw=False
        target_stim.autoDraw=False
        distractor_stim.autoDraw=False
        for placeholder in placeholdersDia:
            placeholder.autoDraw=False
        for placeholder in placeholdersCirc:
            placeholder.autoDraw=False
        
        win.flip()
        #core.wait(ITI)
        
        for stim in stimuli:
            if (stim.pos[0]==which_circle.pos[0]) and (stim.pos[1]==which_circle.pos[1]):
                target_circle=stim
        if (thisBlock[trial]=='neut' and disAorP=='P') or (thisBlock[trial]==cue_type): #if there is no distractor this trial we want to document that
            for stim in stimuli:
                if (stim.pos[0]==(distractor_stim_clock[0]/vis_deg_multiplier)) and (stim.pos[1]==(distractor_stim_clock[1]/vis_deg_multiplier)):
                    distractor_circle=stim
            stim_loc=(target_circle.name,distractor_circle.name)
            dis_name=distractor_stim.name
        else:
            stim_loc=(target_circle.name,'noDis')
            dis_name='noDis'
        
        # # translating things so that the output to the CSV file is a bit more readable
        if thisBlock[trial]=='neut':
            if disAorP=='A':
                neutCue_type='Absent'
            else:
                neutCue_type='Present'
        else:  
            neutCue_type='Present'
        
        if EEGflag:
            Thistrial_data= {'trialNum':(trial),'trial_type':thisBlock[trial],'dis_type':neutCue_type,'corrResp':corrKey,'subjectResp':key,'trialCorr?':trial_corr,'RT':RT,
                            'Tar,Dis,Other':(target_stim.name,dis_name,other_stim[0].name), 'stim_loc':stim_loc,'ITI':ITI,'trial_trigs':(thistrialFlag,probetrig,resp_trig)}
        else:
            Thistrial_data= {'trialNum':(trial),'trial_type':thisBlock[trial],'dis_type':neutCue_type,'corrResp':corrKey,'subjectResp':key,'trialCorr?':trial_corr,'RT':RT, 
                            'Tar,Dis,Other':(target_stim.name,dis_name,other_stim[0].name),'stim_loc':stim_loc,'ITI':ITI,'trial_trigs':'None'}
        trialDataList.append(Thistrial_data)
        
        print(Thistrial_data)
        
        key=event.getKeys()
        if key: 
            if key[0]=='escape': 
                win.close()
                core.quit()
                print('FORCED QUIT')
        
        #if EEGflag:
        #    win.callOnFlip(port.write,ITI_trig)
        #    
        #core.wait(ITI) #ITI--want to jitter this?, with an average of 4 seconds
        
        blocks.update({str(block):trialDataList})
        if block==0:
            make_csv(filename,blocks,thisRunNum,color_code,expStart=True)
        else:
            make_csv(filename,blocks,thisRunNum,color_code,expStart=False)
        
        wait_here(ITI)
        
    if EEGflag:
        port.write(stopBlockflag)
    if block==int(len(stimList_blocks)/2)-1:
        exit_msg= visual.TextStim(win, pos=[0, .5],units='norm', text='You are halfway through the study!')
        exit_msg3=visual.TextStim(win, pos=[0,-0.5],units='norm',text='Please take a break and, when done, call the experimenter over to continue')
        exit_msg.draw() 
        exit_msg3.draw()
        win.flip()
        event.waitKeys(keyList=['z'])


##################################################################################################################################################################
###############    CALL FUNCTIONS     ############################################################################################################################
##################################################################################################################################################################


## make sure everything looks ok with experimenter input
cue_type, thisRunNum, refresh_rate,color_code,visit_num = checkExpInfo(expInfo)

## set up experiment triggers
if EEGflag:
    port=serial.Serial('COM6',baudrate=115200)
    port.close()
    startSaveflag=bytes([201])
    startBlockflag=bytes([133])
    stopBlockflag=bytes([135])
    stopSaveflag=bytes([255])
    cue_trigDict={'dis_cue_trig': 101,
                  'tar_cue_trig':105,
                  'neut_cue_trig':109,}
    
    delay_one_trig=137
    ITI_trig=127
    subNonRespTrig=129
    subRespTrig=131
    response_period_trig=141
    
    probe_trigDict={'neutA_probe_trig': 113,
                  'neutP_probe_trig':115,
                  'tarP_probe_trig':117,
                  'disP_probe_trig':119}
    
    other_trigDict={ 'ITI_trig':ITI_trig,'subNonRespTrig':subNonRespTrig,'subRespTrig':subRespTrig,'delay_one_trig':delay_one_trig,'response_period_trig':response_period_trig}

if EEGflag:
    port.open()
    #win.callonFlip(pport.setData,delay1trig)
    port.write(startSaveflag)
    #port.close()
    
filename='Z:/Alpha/AlphaStudy_new/Data/EEG_experiments/alpha_ColorConstant_Sledgehammer_Foster_data/Raw/behavDat'+u'/%s_%s_%s_block%s_visit%s_%s' % (expInfo['subject'], expName, cue_type,thisRunNum,visit_num,expInfo['date'])


## load stimuli
images, images_names, fixation, stimuli, left_stim, right_stim, neut_color, dist_color, bars, target_color,placeholdersDia,placeholdersCirc = set_stimuli_params(win, color_code,no_stim,vis_deg_cue)

## load trials and blocks
stimList_blocks, cuePosList, neutCue, bar_ori = generate_trial_params(cue_type, no_stim, num_blocks) # default n_neut=32, n_cue=32
#stimList_blocks, cuePosList, neutCue, bar_ori = generate_trial_params(cue_type, no_stim, num_blocks, n_neut=10, n_cue=8) ## only for the purpose of piloting shorter blocks

## if this is the first time we're intializing the script, run through the practice 
if thisRunNum=='1':
    ## display instructions
    display_instructions(cue_type)
    pracCond(n_practrials=3,demo=True)
    pracCond(n_practrials=10,demo=False)

## Enter block loop
print(len(stimList_blocks))
for block in range(len(stimList_blocks)):
    print
    runBlock(stimList_blocks, neutCue, cuePosList, block, bar_ori)

if EEGflag:
    port.write(stopSaveflag)
    port.close()

for stim in stimuli:
    stim.autoDraw=False
fixation.autoDraw=False
 
exit_msg= visual.TextStim(win, pos=[0, .5],units='norm', text='Thank you for participating in our experiment!')
exit_msg2= visual.TextStim(win, pos=[0, 0], units='norm',text='Your time and cooperation is greatly appreciated.')
exit_msg3=visual.TextStim(win, pos=[0,-0.5],units='norm',text='Press any key to exit')
exit_msg.draw()
exit_msg2.draw() 
exit_msg3.draw()

win.flip()
event.waitKeys()