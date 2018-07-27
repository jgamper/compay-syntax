function [ patch ] = read_jp2_region( image_path, level, patch_rect )
    % Read a patch of the image at a given level.
    % patch_rect specifies corners of patch [x1, x2, y1, y2], in frame of level 0.
    % TODO: Check is patch_rect coordinates are in frame of level 0!
    pixel_region = {[patch_rect(1), patch_rect(2)], [patch_rect(3), patch_rect(4)]};
    patch = imread(image_path, 'ReductionLevel', level, 'PixelRegion', pixel_region);
end
