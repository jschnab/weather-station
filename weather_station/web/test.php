<?php
phpinfo();
if (extension_loaded("gd")) {
	printf("extension loaded");
} else {
	printf("extension not loaded");
}
?>
