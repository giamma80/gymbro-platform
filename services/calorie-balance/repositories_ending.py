        except Exception as e:
            logger.error(f"Failed to get trends for {user_id}: {e}")
            return {}