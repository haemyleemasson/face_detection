clearvars all; close all; clc;
fileName = 'face.json' % your jason file name
fid = fopen(fileName); 
raw = fread(fid,inf); 
str = char(raw'); 
fclose(fid);
data = jsondecode(str); % data will contain the results 

% you can change the value. 
% AWS rekognition dectects the face if the condifence score is higher than 50.
threshold=99;

for i=1:length(data)
    if data(i).face.Confidence < threshold 
       data(i).time=NaN 
    end
end

% making an onset file for fMRI analysis 
for i=1:length(data)
onset(i)=data(i).time;
end
onset=sort(onset)';
onset=fix((onset/1000)+1); % fix(2.3) -> 2; fix(3.8) -> 3; you could also choose round function. 
face_onset=unique(onset,'first');
face_onset(isnan(uni_onset))=[];

save('face_onset.mat',face_onset)
