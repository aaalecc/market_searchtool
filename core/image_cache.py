"""
Image caching module for Market Search Tool
Downloads and caches product images locally for faster GUI loading.
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Optional, Tuple
import requests
from PIL import Image, ImageOps
import threading
from queue import Queue, Empty
import time

logger = logging.getLogger(__name__)

class ImageCache:
    """Thread-safe image cache for product images."""
    
    def __init__(self, cache_dir: str = "data/image_cache", max_size_mb: int = 500):
        """
        Initialize the image cache.
        
        Args:
            cache_dir: Directory to store cached images
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self.lock = threading.Lock()
        self.processing_queue = Queue()
        self.processing_thread = None
        self.stop_processing = False
        
        # Start background processing thread
        self._start_processing_thread()
        
        logger.info(f"Image cache initialized at {self.cache_dir}")
    
    def _start_processing_thread(self):
        """Start background thread for processing images."""
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
    
    def _process_queue(self):
        """Background thread to process image queue."""
        while not self.stop_processing:
            try:
                # Get item from queue with timeout
                item = self.processing_queue.get(timeout=1)
                if item is None:  # Stop signal
                    break
                
                image_url, callback = item
                try:
                    cached_path = self._download_and_process_image(image_url)
                    if callback:
                        callback(cached_path)
                except Exception as e:
                    logger.error(f"Failed to process image {image_url}: {e}")
                    if callback:
                        callback(None)
                finally:
                    self.processing_queue.task_done()
                    
            except Empty:
                # This is expected when no items are in the queue
                continue
            except Exception as e:
                if not self.stop_processing:
                    logger.error(f"Error in image processing thread: {e}")
                    # Add a small delay to prevent tight error loops
                    time.sleep(0.1)
    
    def _get_image_hash(self, image_url: str) -> str:
        """Generate a hash for the image URL."""
        return hashlib.md5(image_url.encode()).hexdigest()
    
    def _get_cached_path(self, image_url: str) -> Path:
        """Get the cached file path for an image URL."""
        image_hash = self._get_image_hash(image_url)
        return self.cache_dir / f"{image_hash}.png"
    
    def _download_and_process_image(self, image_url: str) -> Optional[str]:
        """Download and process an image, returning the local path."""
        cached_path = self._get_cached_path(image_url)
        
        # Check if already cached
        if cached_path.exists():
            return str(cached_path)
        
        try:
            # Download image
            response = requests.get(image_url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Process image
            with Image.open(response.raw) as img:
                # Convert to RGBA
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Resize to target size while maintaining aspect ratio
                target_size = (220, 140)
                img = ImageOps.contain(img, target_size, method=Image.LANCZOS)
                
                # Create background
                background = Image.new("RGBA", target_size, (62, 62, 62, 255))
                background.paste(img, ((target_size[0] - img.width) // 2, (target_size[1] - img.height) // 2))
                
                # Save processed image
                background.save(cached_path, "PNG", optimize=True)
                
                # Check cache size and clean if needed
                self._cleanup_cache()
                
                logger.debug(f"Cached image: {image_url} -> {cached_path}")
                return str(cached_path)
                
        except requests.RequestException as e:
            logger.error(f"Network error downloading image {image_url}: {e}")
            return None
        except (OSError, IOError) as e:
            logger.error(f"File system error processing image {image_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to download/process image {image_url}: {e}")
            return None
    
    def _cleanup_cache(self):
        """Clean up cache if it exceeds maximum size."""
        try:
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.png"))
            
            if total_size > self.max_size_bytes:
                # Get all files sorted by modification time (oldest first)
                files = sorted(self.cache_dir.glob("*.png"), key=lambda x: x.stat().st_mtime)
                
                # Remove oldest files until under limit
                for file in files:
                    file.unlink()
                    total_size -= file.stat().st_size
                    if total_size <= self.max_size_bytes * 0.8:  # Leave 20% buffer
                        break
                        
                logger.info(f"Cleaned up image cache, removed {len(files)} files")
                
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
    
    def get_cached_image(self, image_url: str, callback: Optional[callable] = None) -> Optional[str]:
        """
        Get cached image path, downloading if necessary.
        
        Args:
            image_url: URL of the image to cache
            callback: Optional callback function to call when processing is complete
            
        Returns:
            Local path to cached image, or None if not available
        """
        if not image_url or not isinstance(image_url, str):
            return None
        
        # Basic URL validation
        if not image_url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid image URL format: {image_url}")
            return None
        
        cached_path = self._get_cached_path(image_url)
        
        # If already cached, return immediately
        if cached_path.exists():
            return str(cached_path)
        
        # If callback provided, process in background
        if callback:
            self.processing_queue.put((image_url, callback))
            return None  # Return None immediately, callback will be called when ready
        
        # Otherwise, process synchronously
        with self.lock:
            return self._download_and_process_image(image_url)
    
    def preload_images(self, image_urls: list[str]) -> None:
        """
        Preload a list of images in the background.
        
        Args:
            image_urls: List of image URLs to preload
        """
        valid_urls = []
        for image_url in image_urls:
            if (image_url and 
                isinstance(image_url, str) and 
                image_url.startswith(('http://', 'https://'))):
                valid_urls.append(image_url)
            else:
                logger.debug(f"Skipping invalid image URL: {image_url}")
        
        for image_url in valid_urls:
            self.processing_queue.put((image_url, None))
        
        if valid_urls:
            logger.debug(f"Queued {len(valid_urls)} valid images for preloading")
    
    def clear_cache(self) -> None:
        """Clear all cached images."""
        with self.lock:
            for file in self.cache_dir.glob("*.png"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete {file}: {e}")
            logger.info("Image cache cleared")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        try:
            files = list(self.cache_dir.glob("*.png"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                'file_count': len(files),
                'total_size_mb': total_size / (1024 * 1024),
                'max_size_mb': self.max_size_bytes / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'file_count': 0, 'total_size_mb': 0, 'max_size_mb': 0}
    
    def shutdown(self):
        """Shutdown the image cache and stop processing thread."""
        self.stop_processing = True
        self.processing_queue.put(None)  # Stop signal
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("Image cache shutdown complete")
    
    def remove_cached_image(self, cached_path: str) -> bool:
        """
        Remove a specific cached image file.
        
        Args:
            cached_path: Path to the cached image file
            
        Returns:
            True if file was removed successfully
        """
        try:
            if os.path.exists(cached_path):
                os.remove(cached_path)
                logger.debug(f"Removed cached image: {cached_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove cached image {cached_path}: {e}")
            return False
    
    def remove_cached_images(self, cached_paths: list[str]) -> int:
        """
        Remove multiple cached image files.
        
        Args:
            cached_paths: List of paths to cached image files
            
        Returns:
            Number of files successfully removed
        """
        removed_count = 0
        for cached_path in cached_paths:
            if self.remove_cached_image(cached_path):
                removed_count += 1
        return removed_count
    
    def cleanup_orphaned_cache_files(self, db_manager) -> int:
        """
        Clean up cache files that are no longer referenced in the database.
        
        Args:
            db_manager: Database manager instance
            
        Returns:
            Number of orphaned files removed
        """
        try:
            # Get all cached image paths from database
            referenced_paths = set()
            
            # Get from search_results
            results = db_manager.get_search_results(limit=10000)  # Get all results
            for item in results:
                if item.get('cached_image_path'):
                    referenced_paths.add(item['cached_image_path'])
            
            # Get from saved_search_items
            saved_searches = db_manager.get_saved_searches()
            for saved_search in saved_searches:
                items = db_manager.get_saved_search_items(saved_search['id'])
                for item in items:
                    if item.get('cached_image_path'):
                        referenced_paths.add(item['cached_image_path'])
            
            # Get from new_items
            new_items = db_manager.get_new_items(limit=10000)  # Get all new items
            for search_name, items in new_items.items():
                for item in items:
                    if item.get('cached_image_path'):
                        referenced_paths.add(item['cached_image_path'])
            
            # Find orphaned files
            orphaned_files = []
            for cache_file in self.cache_dir.glob("*.png"):
                if str(cache_file) not in referenced_paths:
                    orphaned_files.append(str(cache_file))
            
            # Remove orphaned files
            removed_count = 0
            for orphaned_file in orphaned_files:
                if self.remove_cached_image(orphaned_file):
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} orphaned cache files")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned cache files: {e}")
            return 0

# Global instance
_image_cache = None

def get_image_cache() -> ImageCache:
    """Get the global image cache instance."""
    global _image_cache
    if _image_cache is None:
        _image_cache = ImageCache()
    return _image_cache

def shutdown_image_cache():
    """Shutdown the global image cache."""
    global _image_cache
    if _image_cache:
        _image_cache.shutdown()
        _image_cache = None

def cleanup_orphaned_cache_files(db_manager) -> int:
    """
    Clean up cache files that are no longer referenced in the database.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Number of orphaned files removed
    """
    image_cache = get_image_cache()
    return image_cache.cleanup_orphaned_cache_files(db_manager) 