function [ level_dimensions, level_downsamples, level_count] = get_jp2_info( image_path )
    % Get info about JP2 slide.
    info = imfinfo(image_path);
    level_count = info.WaveletDecompositionLevels;
    for i = 0 : level_count
        level_downsamples(i+1,:) = 2^i;
        level_dimensions(i+1,:) = int32([info.Height/2^i, info.Width/2^i]);
    end
end
