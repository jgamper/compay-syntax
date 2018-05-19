function [ batch ] = read_batch_region( image_path, level, patch_rect )
% batch_rect – array of [x1, x2, y1, y2]
    batch = [];
    patch_count = size(patch_rect,1);
    parfor i = 1 : patch_count 
        pixel_region = {[patch_rect(i,1),patch_rect(i,2)],[patch_rect(i,3),patch_rect(i,4)]};
        batch(i,:,:,:) = imread(image_path,'ReductionLevel',level,'PixelRegion',pixel_region);
    end
end

