function [ image ] = load_whole( image_path, level )

    image = imread(image_path,'ReductionLevel',level);
end
