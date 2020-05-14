function [ image ] = read_jp2( image_path, level )
    % Read the whole image at a given level.
    image = imread(image_path, 'ReductionLevel', level);
end
